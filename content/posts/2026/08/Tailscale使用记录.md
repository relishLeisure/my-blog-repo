---
title: "Tailscale使用记录"
date: 2026-08-28T17:57:29+08:00
draft: false
slug: ""
categories: [软件]
---



# 作为流量转发节点

**Linux下载安装Tailscale**

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

**设置流量出口节点 Exit Node**，其他机器流量经过这个设备转发

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

**其他设备配置**

Windows

右键 -- Exit Node -- 选择设备

Linux

```bash
sudo tailscale up --exit-node=<这台Linux的Tailscale IP或设备名>
```

