---
title: "Linux系统管理"
date: 2026-09-15T14:52:28+08:00
draft: true
slug: "Linux系统管理"
categories: []
---

# Linux 服务器硬件与系统资源检查记录
# 1. 操作系统版本
## 命令

```bash
cat /etc/os-release
```
查看内核版本：

```bash
uname -a
```
## 输出
```
PRETTY_NAME="Ubuntu 24.04.2 LTS"
NAME="Ubuntu"
VERSION_ID="24.04"
VERSION="24.04.2 LTS (Noble Numbat)"
VERSION_CODENAME=noble
ID=ubuntu
ID_LIKE=debian
HOME_URL="https://www.ubuntu.com/"
SUPPORT_URL="https://help.ubuntu.com/"
BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
UBUNTU_CODENAME=noble
LOGO=ubuntu-logo
```
```
Linux wsco-X11DAi-N 6.11.0-21-generic #21~24.04.1-Ubuntu SMP PREEMPT_DYNAMIC Mon Feb 24 16:52:15 UTC 2 x86_64 x86_64 x86_64 GNU/Linux
```
# 2. CPU 信息
## 命令
```
lscpu
```
## 输出
```
架构：                    x86_64
  CPU 运行模式：          32-bit, 64-bit
  Address sizes:          46 bits physical, 48 bits virtual
  字节序：                Little Endian
CPU:                      72
  在线 CPU 列表：         0-71
厂商 ID：                 GenuineIntel
  型号名称：              Intel(R) Xeon(R) Gold 6151 CPU @ 3.00GHz
    CPU 系列：            6
    型号：                85
    每个核的线程数：      2
    每个座的核数：        18
    座：                  2
    步进：                4
    CPU(s) scaling MHz:   94%
```
# 3. GPU 信息

## 命令

```
nvidia-smi
```
# 4. CPU 负载

## 命令

查看当前 CPU 使用情况：

```
top
# 更推荐：
htop
```

查看当前平均负载：

```
uptime
```

查看最近 1、5、15 分钟负载：

```
cat /proc/loadavg
```

## 输出

```
top - 15:47:56 up 15 days, 43 min, 15 users,  load average: 135.87, 137.26, 135.68
任务: 946 total,   5 running, 941 sleeping,   0 stopped,   0 zombie
%Cpu(s): 98.4 us,  0.6 sy,  0.0 ni,  1.0 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st 
MiB Mem : 450683.9 total, 333056.8 free,  30707.7 used,  90178.5 buff/cache     
MiB Swap:   8192.0 total,   8192.0 free,      0.0 used. 419976.2 avail Mem 
```

# 5. 内存

## 命令

```
free -h
```

查看更详细的内存信息：

```
cat /proc/meminfo
```

## 输出

```
               total        used        free      shared  buff/cache   available
内存：         
交换：         
```

# 6. 硬盘 / 存储空间

## 命令

查看磁盘空间：

```
df -h
```

查看磁盘和分区：

```
lsblk
```

## 输出

```
文件系统        大小  已用  可用 已用% 挂载点
tmpfs            45G  4.0M   45G    1% /run
/dev/nvme0n1p2  937G  775G  115G   88% /
```

```
NAME        MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
loop0         7:0    0     4K  1 loop /snap/bare/5
```

# 7. 网络连接

## 命令

查看**网卡及 IP**：

```
ip addr
```

查看**网卡状态**：

```
ip -br addr
```

查看**路由**：

```
ip route
```

查看**监听端口**：

```
ss -lntup
```

查看当前**网络连接**：

```
ss -ant
```

查看**网络接口流量统计**：

```
ip -s link
```

# 8. 当前连接用户

## 命令

```
who
```

# 9. 定时任务

## 当前用户 Cron

```
crontab -l
```

## 系统 Cron

```
cat /etc/crontab
```

## systemd 定时任务

```
systemctl list-timers --all
```



