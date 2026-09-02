---
title: "Tailscale使用记录"
date: 2026-08-28T17:57:29+08:00
draft: true
slug: ""
categories: [软件]
---



# 设置流量转发节点

### **Linux下载安装Tailscale**

```bash
sudo mkdir -p /etc/apt/sources.list.d/
curl -fsSL https://tailscale.com/install.sh | sh
```

**登录**

```bash
sudo tailscale up
```

**开启ip转发**

```bash
echo 'net.ipv4.ip_forward = 1' | sudo tee -a /etc/sysctl.d/99-tailscale.conf
echo 'net.ipv6.conf.all.forwarding = 1' | sudo tee -a /etc/sysctl.d/99-tailscale.conf
sudo sysctl -p /etc/sysctl.d/99-tailscale.conf
```

### **设置流量出口节点 Exit Node**

其他机器流量经过这个设备转发

```c++
sudo tailscale up --advertise-exit-node
```

**在 Tailscale 控制面板中批准 Authorization**

出于安全考虑，宣告后并不会立刻生效，必须在后台手工允许：

1. 打开 [Tailscale Admin Console (Machines 页面)](https://login.tailscale.com/admin/machines)。
2. 找到你刚配置的这台 Linux 设备。
3. 点击设备右侧的 **`...`** (更多选项) -> 选择 **Edit route settings**。
4. 勾选 **Use as exit node**。
5. 点击 **Save**。

### **其他设备配置**

Windows

右键 -- Exit Node -- 选择设备

Linux

```bash
sudo tailscale up --exit-node=<这台Linux的Tailscale IP或设备名>
```

---

# Exit Node 卡顿排查

> Tailscale  作为exit node 的设备， 只有单核1g内存，其他设备访问网络卡顿，
> 开启exit node 走 linux 之后，网络十分的慢，网页打不开，考虑排查问题；
> 考虑先查看 linux 系统设备和网络资源

设备系统资源查看

```bash
# cpu 资源占用
top
# 结果显示
ubuntu@10-40-95-220:~$ top
top - 15:39:18 up 3 days, 21:50,  3 users,  load average: 0.00, 0.00, 0.00
Tasks:  98 total,   1 running,  97 sleeping,   0 stopped,   0 zombie
%Cpu(s):  0.7 us,  0.3 sy,  0.0 ni, 99.0 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
MiB Mem :    960.6 total,    178.4 free,    351.5 used,    582.4 buff/cache
MiB Swap:      0.0 total,      0.0 free,      0.0 used.    609.1 avail Mem

    PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
   2544 root      20   0 1422384  56964  24320 S   1.0   5.8   3:23.16 tailscaled
  65122 ubuntu    20   0   12344   5760   3584 R   0.3   0.6   0:00.02 top
      1 root      20   0   22412  11136   7056 S   0.0   1.1   0:25.52 systemd

# 观察 si (swap in) 和 so (swap out) 列。如果这两个数值在网络传输时持续大于 0，说明 1GB 内存耗尽，系统正向磁盘频繁读写 Swap，会导致系统严重卡顿甚至死锁。
vmstat 1 5
# 没有问题
ubuntu@10-40-95-220:~$ vmstat 1 5
procs -----------memory---------- ---swap-- -----io---- -system-- -------cpu-------
 r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st gu
 1  0      0 182640  65844 530556    0    0   486    18   51    0  0  0 99  0  0  0
 0  0      0 182640  65844 530560    0    0     0     0  573  604  1  1 98  0  0  0
 0  0      0 182640  65844 530560    0    0     0    52  420  496  1  2 97  0  0  0
 0  0      0 182640  65844 530560    0    0     0    44  157  160  0  0 100  0  0  0
 0  0      0 182640  65844 530556    0    0     0     4  178  231  0  0 100  0  0  0

```

网络

```bash
# 网络
ip -s link show eth0
ip -s link show tailscale0
# 
ubuntu@10-40-95-220:~$ ip -s link show eth0
ip -s link show tailscale0
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1452 qdisc pfifo_fast state UP mode DEFAULT group default qlen 1000
    link/ether 52:54:00:11:80:f5 brd ff:ff:ff:ff:ff:ff
    RX:  bytes packets errors dropped  missed   mcast
     837765237 1266218      0       0       0       0
    TX:  bytes packets errors dropped carrier collsns
     327923527 1005931      0       0       0       0
3: tailscale0: <POINTOPOINT,MULTICAST,NOARP,UP,LOWER_UP> mtu 1280 qdisc pfifo_fast state UNKNOWN mode DEFAULT group default qlen 500
    link/none
    RX:  bytes packets errors dropped  missed   mcast
      21266173  133651      0       0       0       0
    TX:  bytes packets errors dropped carrier collsns
     168118233  142024      0       0       0       0
```

```bash
ubuntu@10-40-95-220:~$ tailscale status
100.120.240.21  ucloud-tokyo-till-0928  729505530@  linux    idle; offers exit node                 
100.125.69.36   iphone-11               729505530@  iOS      offline, last seen 3d ago              
100.88.164.45   pcofcg                  729505530@  windows  active; relay "hkg", tx 5695616 rx 2242248

ubuntu@10-40-95-220:~$ tailscale netcheck
2026/09/01 15:45:02 portmap: monitor: gateway and self IP changed: gw=10.40.0.1 self=10.40.95.220
Report:
        * Time: 2026-09-01 15:45:04.195906728+09:00
        * UDP: true
        * IPv4: yes, 152.32.145.19:37105
        * IPv6: no, but OS has support
        * MappingVariesByDestIP: false
        * PortMapping:
        * CaptivePortal: false
        * Nearest DERP: Tokyo
        * DERP latency:
                - tok: 2.8ms   (Tokyo)
                - hkg: 53.3ms  (Hong Kong)
                - sin: 68.3ms  (Singapore)
                - sea: 90.4ms  (Seattle)
                - lax: 101.2ms (Los Angeles)
                - sfo: 106.6ms (San Francisco)
                - den: 126.5ms (Denver)
                - dfw: 132.8ms (Dallas)
                - ord: 140.6ms (Chicago)
                - tor: 145.4ms (Toronto)
                - hnl: 146.8ms (Honolulu)
                - nyc: 153ms   (New York City)
                - iad: 155.6ms (Ashburn)
                - mia: 160.1ms (Miami)
                - syd: 210.5ms (Sydney)
                - lhr: 224ms   (London)
                - ams: 228.7ms (Amsterdam)
                - par: 234.3ms (Paris)
                - fra: 239.2ms (Frankfurt)
                - blr: 245.2ms (Bengaluru)
                - nue: 245.4ms (Nuremberg)
                - mad: 255.8ms (Madrid)
                - waw: 258.1ms (Warsaw)
                - hel: 260.7ms (Helsinki)
                - sao: 291.4ms (São Paulo)
                - dbi: 329.7ms (Dubai)
                - jnb: 383.4ms (Johannesburg)
                - nai: 420.4ms (Nairobi)

```

windows 设备

```powershell
(base) PS C:\Users\72950> tailscale netcheck
2026/09/01 15:02:12 portmap: monitor: gateway and self IP changed: gw=10.203.128.1 self=10.203.208.115

Report:
        * Time: 2026-09-01 15:02:16.8349557+08:00
        * UDP: true
        * IPv4: yes, 153.3.60.172:57209
        * IPv6: no, but OS has support
        * MappingVariesByDestIP: true
        * PortMapping:
        * CaptivePortal: false
        * Nearest DERP: Hong Kong
        * DERP latency:
                - hkg: 163.3ms (Hong Kong)
                - sfo: 172.7ms (San Francisco)
                - waw: 172.8ms (Warsaw)
                - nue: 174.8ms (Nuremberg)
                - den: 189ms   (Denver)
                - lax: 189.3ms (Los Angeles)
                - sea: 197.1ms (Seattle)
                - blr: 211.4ms (Bengaluru)
                - dfw: 226.9ms (Dallas)
                - ord: 227.4ms (Chicago)
                - fra: 227.4ms (Frankfurt)
                - tok: 227.4ms (Tokyo)
                - ams: 227.4ms (Amsterdam)
                - tor: 234.3ms (Toronto)
                - mia: 239.2ms (Miami)
                - lhr: 239.2ms (London)
                - par: 239.8ms (Paris)
                - hnl: 239.8ms (Honolulu)
                - nyc: 253.2ms (New York City)
                - mad: 284.3ms (Madrid)
                - dbi: 290.4ms (Dubai)
                - iad: 295.4ms (Ashburn)
                - sin: 299.9ms (Singapore)
                - hel: 325ms   (Helsinki)
                - syd: 328.9ms (Sydney)
                - sao: 346.9ms (São Paulo)
                - nai: 347.8ms (Nairobi)
                - jnb: 411.4ms (Johannesburg)
```

### 问题

问题的最核心原因：Windows 客户端的 `netcheck` 显示 **`MappingVariesByDestIP: true`**。

这意味着你的 Windows 电脑处于**对称 NAT**（通常是企业网、校园网、运营商大内网或 5G 热点）环境下。在对称 NAT 下，客户端的 UDP 端口是动态随机变化的。此时想要建立 Tailscale 直连，**云服务器（Exit Node）必须拥有一个完全公网开放的固定 UDP 端口（默认 41641）**。由于你尚未在云服务器上放行该端口，两边互相“打洞”必定失败，只能退化为慢速的中继（Relay）。

### 解决过程

### 1. 在 UCloud 控制台放行端口（轻量应用服务专属位置）

UCloud 的“轻量应用服务”为了简化操作，**没有**全局的“安全组”概念。防火墙规则直接绑定在单台服务器实例上。

<img src="Tailscale使用记录.assets/image-20260901150603246.png" alt="image-20260901150603246" style="zoom:50%;" />

添加规则

<img src="Tailscale使用记录.assets/image-20260901150821249.png" alt="image-20260901150821249" style="zoom:50%;" />

### 2. 放行 Linux 内部系统防火墙

有时即便云控制台放行了，Linux 系统自身的防火墙仍会拦截。请在你的 Ubuntu 服务器上执行以下命令放行：

```bash
# 如果使用 ufw (Ubuntu 默认)
sudo ufw allow 41641/udp

# 如果使用 iptables
sudo iptables -I INPUT -p udp --dport 41641 -j ACCEPT
```

重启tailscale

```bash
sudo systemctl restart tailscaled
```

检验结果

```powershell
# windows 端
tailscale status
# 
(base) PS C:\Users\72950> tailscale status
100.88.164.45   pcofcg                  729505530@  windows  -
100.125.69.36   iphone-11               729505530@  iOS      offline, last seen 3d ago
100.120.240.21  ucloud-tokyo-till-0928  729505530@  linux    idle; offers exit node
```

开启exit node 之后

```powershell
(base) PS C:\Users\72950> tailscale status
100.88.164.45   pcofcg                  729505530@  windows  -                                      
100.125.69.36   iphone-11               729505530@  iOS      offline, last seen 3d ago              
100.120.240.21  ucloud-tokyo-till-0928  729505530@  linux    active; exit node; relay "tok", tx 34004 rx 27100
```

### 3.DNS 配置

**关闭Tailscale DNS**

**校园网 DNS 污染**

- **现象**：开启 Exit Node 后，能够 Ping 通 IP（如 `8.8.8.8`），但访问域名全部超时。
- **原因**：校园网默认 DNS 拦截了你的域名请求，返回了虚假 IP（如 `174.132.x.x`）。
- **解决**：在 Windows 本地物理网卡手动指定公共 DNS（`8.8.8.8`），并刷新本地 DNS 缓存，绕过了校园网的劫持。

> 修改dns的步骤
>
> 1. 按下 `Win + R` 键，输入 `ncpa.cpl` 并回车（打开网络连接窗口）。
> 2. 找到你连接校园网的网卡（例如 **以太网** 或 **WLAN / Wi-Fi**），右键点击选择 **属性**。
> 3. 在列表中双击 **Internet 协议版本 4 (TCP/IPv4)**。
> 4. IP 地址保持“自动获得 IP 地址”不变。
> 5. 下半部分勾选 **使用下面的 DNS 服务器地址**：**首选 DNS 服务器**：`8.8.8.8`（Google 公共 DNS）**备用 DNS 服务器**：`1.1.1.1`（Cloudflare DNS）
> 6. 点击 **确定** 保存。

```cmd
# 刷新本地 DNS 缓存
ipconfig /flushdns
```

### 4.**Linux Exit Node 转发配置**

- **现象**：默认开启 Exit Node 并不足以支撑完整的网页浏览。
- **解决**：
  - **内核转发**：`ip_forward = 1` 允许数据包穿透系统。
  - **NAT 伪装**：`iptables MASQUERADE` 让内网数据包伪装成东京公网 IP 出海。
  - **MSS 裁剪**：`TCPMSS --clamp-mss-to-pmtu` 解决了 VPN 隧道特有的 MTU 溢出问题，防止大流量数据包被中途丢弃。
