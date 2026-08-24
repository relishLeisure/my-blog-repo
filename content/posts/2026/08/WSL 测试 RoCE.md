---
title: "WSL 测试 RoCE"
date: 2026-08-24T17:38:02+08:00
draft: false
slug: 
categories: [RDMA,笔记,实验]
---

# WSL 架构 Debian 环境 Soft-RoCE RDMA 开发环境

## 第零步：检测 RXE 是否安装

```bash
zcat /proc/config.gz | grep -i RXE
```

## 第一步：安装 Debian 编译依赖

```bash
cd ~			# 先回到 Linux 用户主目录并安装依赖 codeBash  downloadcontent_copy   expand_less
sudo apt update
sudo apt install build-essential flex bison dwarves libssl-dev libelf-dev bc libncurses-dev pkg-config
```

下载源码

https://kernel.org/   下载LTS版本

```bash
cd ~
truman@pcofcg:~$ pwd
/home/truman

# 1. 从官方下载 Linux Kernel 6.1 系列源码 (这里以 6.1.84 为例)
wget https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.6.135.tar.xz
# 或者手动  https://kernel.org/   下载LTS版本

tar -xf linux-6.6.135.tar.xz
cd linux-6.6.135/
```

## 第三步：下载 WSL 配置文件并启用 Soft-RoCE

```bash
# 1. 下载微软官方内核配置文件
wget https://raw.githubusercontent.com/microsoft/WSL2-Linux-Kernel/linux-msft-wsl-6.6.y/arch/x86/configs/config-wsl -O arch/x86/configs/config-wsl

# 2. 打开图形化内核配置菜单
make menuconfig KCONFIG_CONFIG=arch/x86/configs/config-wsl
```

图形化操作说明

```markdown
1.操作
在弹出的蓝色图形化界面中，您需要做以下操作来开启 RDMA：
按键盘的 / 键打开搜索框，输入 RDMA_RXE 并回车。
找到 Software RDMA over Ethernet (RoCE) driver 选项。
按照提示路径，进入菜单（一般在 Device Drivers -> InfiniBand support 下）。
2.修改
将以下几项选中（按空格键，使其前面变成 <*> 或 [*]）：
InfiniBand support (开启 InfiniBand 支持)
InfiniBand userspace MAD support
InfiniBand userspace access (verbs and CM) (对应教程里的 InfiniBand userspace, RDMA verbs transport library)
Software RDMA over Ethernet (RoCE) driver (对应 Soft RoCE)
3.注意
配置完成后，利用左右方向键选中底部的 <Save> 并回车保存（默认保存为 arch/x86/configs/config-wsl，不要改名字），然后一直 <Exit> 退出。
```

## 第四步：编译内核并拷贝到 Windows

```bash
# 1. 编译内核（时间较长，取决于您的 CPU 性能，-j 后面的参数会自动利用全核心）
make KCONFIG_CONFIG=arch/x86/configs/config-wsl -j$(nproc)

# 2. 将编译好的内核文件直接拷贝到您的 Windows 桌面上
cp arch/x86/boot/bzImage /mnt/c/Users/72950/Desktop/kernel_rxe
```

## 第五步：修改 .wslconfig 替换内核

1. 在 Windows 系统中，打开 `C:\Users\<username>` 文件夹。
2. 新建一个文本文件，命名为 `.wslconfig`（注意前面有个点）。如果已有该文件，直接编辑即可。
3. 在里面填入以下内容并保存（注意路径中的反斜杠需要双写 \\）：

```txt
[wsl2]
kernel=D:\\enviroment\\linux\\kernel_rxe
```

## 第六步：重启 WSL 并验证

在 **Windows 侧的 PowerShell** 中运行以下命令彻底关闭 WSL：

```bash
wsl --shutdown
```

再次打开您的 Debian 终端，输入命令检查内核：

```bash
uname -a		# 如果看到编译日期是今天的时间戳，并且内核名称没有带 -microsoft 标准后缀，说明内核替换成功
truman@pcofcg:/mnt/c/Users/72950$ uname -a
Linux pcofcg 6.6.135-microsoft-standard-WSL2 #3 SMP PREEMPT_DYNAMIC Tue Apr 28 10:30:49 CST 2026 x86_64 GNU/Linux
```

检验RXE(Soft-RoCE)

```BASH
truman@pcofcg:/mnt/c/Users/72950$ zcat /proc/config.gz | grep -i RXE
CONFIG_RDMA_RXE=y

truman@pcofcg:/mnt/c/Users/72950$ zcat /proc/config.gz | grep -i RXE
CONFIG_RDMA_RXE=m
# 是模块 m， 所以手动加载
truman@pcofcg:/mnt/c/Users/72950$ sudo modprobe rdma_rxe
modprobe: FATAL: Module rdma_rxe not found in directory /lib/modules/6.6.135-microsoft-standard-WSL2
# 模块没有安装的话
truman@pcofcg:~/linux-6.6.135$ make modules_prepare
***
*** Configuration file ".config" not found!
***
*** Please run some configurator (e.g. "make oldconfig" or
*** "make menuconfig" or "make xconfig").
***
make[1]: *** [/home/truman/linux-6.6.135/Makefile:784: .config] Error 1
make: *** [Makefile:234: __sub-make] Error 2
truman@pcofcg:~/linux-6.6.135$ rm -rf .config
truman@pcofcg:~/linux-6.6.135$ zcat /proc/config.gz > .config
truman@pcofcg:~/linux-6.6.135$ ls -la .config
-rw-r--r-- 1 truman truman 212542 Apr 28 10:22 .config
truman@pcofcg:~/linux-6.6.135$ nano .config
truman@pcofcg:~/linux-6.6.135$ make modules_prepare
```



## 第七步：配置虚拟网卡和 Soft-RoCE

```bash
# 1. 安装 RDMA 核心工具
sudo apt install rdma-core perftest infiniband-diags ibverbs-utils

# 2. 配置虚拟网卡并分配 IP
sudo ip link add veth0 type veth peer name veth1
sudo ip addr add 192.168.96.110/24 dev veth0
sudo ip addr add 192.168.96.111/24 dev veth1
sudo ip link set veth0 up
sudo ip link set veth1 up

truman@pcofcg:/mnt/c/Users/72950$ ip link show
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP mode DEFAULT group default qlen 1000
    link/ether 00:15:5d:96:a9:dd brd ff:ff:ff:ff:ff:ff
    altname enx00155d96a9dd
3: veth1@veth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP mode DEFAULT group default qlen 1000
    link/ether 26:ba:35:07:2b:f8 brd ff:ff:ff:ff:ff:ff
4: veth0@veth1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP mode DEFAULT group default qlen 1000
    link/ether de:4a:ab:d3:06:fd brd ff:ff:ff:ff:ff:ff

# 3. 允许回环测试
sudo sysctl -w net.ipv4.conf.veth0.accept_local=1
sudo sysctl -w net.ipv4.conf.veth1.accept_local=1

# 4. 将 RXE(Soft-RoCE) 挂载到网卡上
# 将 rxe 设备附加到 veth0 上，命名为 rxe0
sudo rdma link add rxe0 type rxe netdev veth0
sudo rdma link add rxe1 type rxe netdev veth1

# 5. 检查 RDMA 状态
rdma link		# 有结果就成功
ibstat			# 有结果就成功
truman@pcofcg:/mnt/c/Users/72950$ ibv_devices
    device                 node GUID
    ------              ----------------
    rxe0                dc4aabfffed306fd
    rxe1                24ba35fffe072bf8

```



```markdown
SSGP:    拷贝数据的包，ip地址到ip地址，主机之间拷贝数据
IGMP:    局域网之间的ARP
ICMPv6:  类似ARP，进行局域网内的ARP
MDNS:    ？
```

windows抓包都是垃圾包，设备之间的服务发现等包，没真实抓到RoCEv2的包

# WSL内抓包

## RoCEv2

```bash
# 查看 RDMA 绑定的网口
truman@pcofcg:~/dump$ rdma link show
link rxe0/1 state ACTIVE physical_state LINK_UP netdev veth0
link rxe1/1 state ACTIVE physical_state LINK_UP netdev veth1
# 虚拟网口绑定的 ip 地址
truman@pcofcg:~/dump$ ip addr show veth0
# 给 veth 配 IP（直接点对点，不需要网关）
sudo ip addr add 10.0.0.1/24 dev veth0
sudo ip addr add 10.0.0.2/24 dev veth1
```

**服务端**

```bash
# 
# 3. 服务端循环
while true; do rping -s -a 10.0.0.1; done

truman@pcofcg:/mnt/c/Users/72950$ rping -s -a 10.0.0.1 -v
server ping data: rdma-ping-0: ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqr
server ping data: rdma-ping-1: BCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrs
server ping data: rdma-ping-2: CDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrst
server ping data: rdma-ping-3: DEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstu
server ping data: rdma-ping-4: EFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuv
server ping data: rdma-ping-5: FGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvw
server ping data: rdma-ping-6: GHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwx
server ping data: rdma-ping-7: HIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxy
server ping data: rdma-ping-8: IJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz
server ping data: rdma-ping-9: JKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyzA
server DISCONNECT EVENT...
wait for RDMA_READ_ADV state 10
```

**监听端**

```bash
# 
truman@pcofcg:~/dump$ sudo tcpdump -i any udp port 4791 -n
tcpdump: WARNING: any: That device doesn't support promiscuous mode
(Promiscuous mode not supported on the "any" device)
tcpdump: verbose output suppressed, use -v[v]... for full protocol decode
listening on any, link-type LINUX_SLL2 (Linux cooked v2), snapshot length 262144 bytes
14:11:56.574299 veth1 Out IP 10.0.0.2.55410 > 10.0.0.1.4791: UDP, length 280
14:11:56.574304 veth0 In  IP 10.0.0.2.55410 > 10.0.0.1.4791: UDP, length 280
14:11:56.574441 veth0 Out IP 10.0.0.1.55410 > 10.0.0.2.4791: UDP, length 280
14:11:56.574442 veth1 In  IP 10.0.0.1.55410 > 10.0.0.2.4791: UDP, length 280
14:12:06.430103 veth1 Out IP 10.0.0.2.55410 > 10.0.0.1.4791: UDP, length 280
14:12:06.430106 veth0 In  IP 10.0.0.2.55410 > 10.0.0.1.4791: UDP, length 280
14:12:06.430522 veth0 Out IP 10.0.0.1.55410 > 10.0.0.2.4791: UDP, length 280
14:12:06.430526 veth1 In  IP 10.0.0.1.55410 > 10.0.0.2.4791: UDP, length 280
14:12:06.430818 veth1 Out IP 10.0.0.2.55410 > 10.0.0.1.4791: UDP, length 280
14:12:06.430819 veth0 In  IP 10.0.0.2.55410 > 10.0.0.1.4791: UDP, length 280
^C
146 packets captured
146 packets received by filter
0 packets dropped by kernel
# 保存抓包
truman@pcofcg:~/dump$ sudo tcpdump -i veth0 udp port 4791 -n -v -w ./rdma.pcap
tcpdump: listening on veth0, link-type EN10MB (Ethernet), snapshot length 262144 bytes
^C125 packets captured
125 packets received by filter
0 packets dropped by kernel

```

**客户端**

```bash
truman@pcofcg:~/dump$ rping -c -a 10.0.0.1 -I 10.0.0.2 -v -C 10
ping data: rdma-ping-0: ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqr
ping data: rdma-ping-1: BCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrs
ping data: rdma-ping-2: CDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrst
ping data: rdma-ping-3: DEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstu
ping data: rdma-ping-4: EFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuv
ping data: rdma-ping-5: FGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvw
ping data: rdma-ping-6: GHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwx
ping data: rdma-ping-7: HIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxy
ping data: rdma-ping-8: IJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz
ping data: rdma-ping-9: JKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyzA
client DISCONNECT EVENT...
```

## iWARP测试

**注意**

```bash
# 为了避免Soft-RoCE可能造成的干扰，建议先删除RXE设备
sudo rdma link del rxe0
sudo rdma link del rxe1
```

**配置**

```bash
# 1. 配置虚拟网卡并分配 IP
sudo ip link add veth2 type veth peer name veth3
sudo ip addr add 10.1.0.1/24 dev veth2
sudo ip addr add 10.1.0.2/24 dev veth3
sudo ip link set veth2 up
sudo ip link set veth3 up

# 2. 绑定 iWARP 设备
sudo rdma link add siw_0 type siw netdev veth2
sudo rdma link add siw_1 type siw netdev veth3

# 3. 查看设备
# 设备
truman@pcofcg:~/dump$ ibv_devices
    device                 node GUID
    ------              ----------------
    rxe0                dc4aabfffed306fd
    rxe1                24ba35fffe072bf8
    siw_0               648a11fffe6d9f0b
    siw_1               e02999fffe16377a
# 链路
truman@pcofcg:~/dump$ rdma link
link siw_0/1 state ACTIVE physical_state LINK_UP netdev veth2
link siw_1/1 state ACTIVE physical_state LINK_UP netdev veth3
# 详细信息
truman@pcofcg:~/dump$ ibv_devinfo -d siw_0
hca_id: siw_0
        transport:                      iWARP (1)			# 看到传输层协议是 iWARP
```

## perftest

**服务端**

```bash
# -R 表示使用 rdma_cm 建立连接，这是 iWARP 的标准方式。
truman@pcofcg:~/dump$ ib_write_bw -d siw_0 -R

************************************
* Waiting for client to connect... *
************************************
---------------------------------------------------------------------------------------
                    RDMA_Write BW Test
 Dual-port       : OFF          Device         : siw_0
 Number of qps   : 1            Transport type : IW
 Connection type : RC           Using SRQ      : OFF
 PCIe relax order: ON           Lock-free      : OFF
 ibv_wr* API     : OFF          Using DDP      : OFF
 CQ Moderation   : 1
 Mtu             : 1024[B]
 Link type       : Ethernet
 GID index       : 0
 Max inline data : 0[B]
 rdma_cm QPs     : ON
 Data ex. method : rdma_cm
---------------------------------------------------------------------------------------
 Waiting for client rdma_cm QP to connect
 Please run the same command with the IB/RoCE interface IP
---------------------------------------------------------------------------------------
 local address: LID 0000 QPN 0x0004 PSN 0x5e3e06
 GID: 102:138:17:109:159:11:00:00:00:00:00:00:00:00:00:00
 remote address: LID 0000 QPN 0x0003 PSN 0x67ef40
 GID: 102:138:17:109:159:11:00:00:00:00:00:00:00:00:00:00
---------------------------------------------------------------------------------------
 #bytes     #iterations    BW peak[MiB/sec]    BW average[MiB/sec]   MsgRate[Mpps]
 65536      5000             8609.87            6595.36              0.105526
---------------------------------------------------------------------------------------
```

**客户端**

```bash
truman@pcofcg:~/dump$ ib_write_bw -d siw_0 10.1.0.1 -R
---------------------------------------------------------------------------------------
                    RDMA_Write BW Test
 Dual-port       : OFF          Device         : siw_0
 Number of qps   : 1            Transport type : IW
 Connection type : RC           Using SRQ      : OFF
 PCIe relax order: ON           Lock-free      : OFF
 ibv_wr* API     : OFF          Using DDP      : OFF
 TX depth        : 128
 CQ Moderation   : 1
 Mtu             : 1024[B]
 Link type       : Ethernet
 GID index       : 0
 Max inline data : 0[B]
 rdma_cm QPs     : ON
 Data ex. method : rdma_cm
---------------------------------------------------------------------------------------
 local address: LID 0000 QPN 0x0003 PSN 0x67ef40
 GID: 102:138:17:109:159:11:00:00:00:00:00:00:00:00:00:00
 remote address: LID 0000 QPN 0x0004 PSN 0x5e3e06
 GID: 102:138:17:109:159:11:00:00:00:00:00:00:00:00:00:00
---------------------------------------------------------------------------------------
 #bytes     #iterations    BW peak[MiB/sec]    BW average[MiB/sec]   MsgRate[Mpps]
 65536      5000             8609.87            6595.36              0.105526
---------------------------------------------------------------------------------------
```

**监听端**

```bash
# iWARP 抓包（TCP 层）
sudo tcpdump -i veth2 tcp -n -v

# 更精确：iWARP 默认端口是 TCP 5000（rdma_cm）
sudo tcpdump -i veth2 tcp port 5000 -n -v

# 
sudo tcpdump -i any tcp -n
sudo tcpdump -i any tcp -n -v -w ./iwarp_perftest.pcap
```

## rping

**看注意**

**服务端**

```bash
truman@pcofcg:~/dump$ rping -s -a 10.1.0.1 -v
server ping data: rdma-ping-0: ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqr
server ping data: rdma-ping-1: BCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrs
server ping data: rdma-ping-2: CDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrst
server ping data: rdma-ping-3: DEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstu
server ping data: rdma-ping-4: EFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuv
server ping data: rdma-ping-5: FGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvw
server ping data: rdma-ping-6: GHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwx
server ping data: rdma-ping-7: HIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxy
server ping data: rdma-ping-8: IJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz
server ping data: rdma-ping-9: JKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyzA
server DISCONNECT EVENT...
wait for RDMA_READ_ADV state 10
```

**客户端**

```bash
truman@pcofcg:~/dump$ rping -c -a 10.1.0.1 -I 10.1.0.2 -v -C 10
ping data: rdma-ping-0: ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqr
ping data: rdma-ping-1: BCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrs
ping data: rdma-ping-2: CDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrst
ping data: rdma-ping-3: DEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstu
ping data: rdma-ping-4: EFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuv
ping data: rdma-ping-5: FGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvw
ping data: rdma-ping-6: GHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwx
ping data: rdma-ping-7: HIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxy
ping data: rdma-ping-8: IJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz
ping data: rdma-ping-9: JKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyzA
client DISCONNECT EVENT...
```

**监听端**

```bash
truman@pcofcg:~/dump$ sudo tcpdump -i any tcp -n -v -w ./iwarp_rping.pcap
tcpdump: WARNING: any: That device doesn't support promiscuous mode
(Promiscuous mode not supported on the "any" device)
tcpdump: listening on any, link-type LINUX_SLL2 (Linux cooked v2), snapshot length 262144 bytes
Got 90
```

# 抓包结果

## RoCEv2

{{< img src="img/2026/08/WSL 测试 RoCE/RDMA 抓包1.png" alt="图片" >}}

## iWARP perftest

{{< img src="img/2026/08/WSL 测试 RoCE/iwarp_perftest 抓包1.png" alt="图片" >}}

**1. DDP**

- **直接数据放置协议(DDP, Direct Data Placement Protocol)**

相当于RDMA，作用和RDMA一致

**2. MPA**

- **标记 PDU 对齐帧协议（MPA，Marker PDU Aligned Framing Protocol）**

**核心作用**：TCP 是有序的，如果发现包乱序到达，会抛弃新到达的包，要求发送端从丢失的位置开始重传。RoCE 要求是无损的，因此使用MPA弥补这个问题。

MPA 夹在 TCP 和 DDP 之间，负责在 TCP 字节流中插入固定间隔的“标记”（Marker）、添加长度头以及 CRC32 校验码。这使得接收端网卡即便遇到 **Out-of-Order（乱序）到达的 TCP 报文**，也能迅速定位并解析出独立的 DDP 帧。

## iWARP rping

{{< img src="img/2026/08/WSL 测试 RoCE/iwarp_rping 抓包1.png" alt="图片" >}}





