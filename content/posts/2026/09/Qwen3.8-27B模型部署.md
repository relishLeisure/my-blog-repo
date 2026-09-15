---
title: "Qwen3.8 27B模型部署"
date: 2026-09-04T14:55:37+08:00
draft: true
slug: ""
categories: []
---

1

模型可使用`SGLang`、`KTransformers`、`vLLM`部署引擎，社区第三方量化版可使用`Ollama`、`llama.cpp`、`LM Studio`等引擎，本文介绍常用的`vLLM`和`llama.cpp`的详细部署方式（ollama、LM Studio和unsloth底层都是基于llama.cpp，KTransformers是Sglang的分支，主打CPU内存跑模型）。

`SGLang`、`KTransformers`、`vLLM`

`Ollama`、`llama.cpp`、`LM Studio`等引擎 是什么



2

vLLM方式

- 硬件：Nvidia A30 * 2；显存24G * 2 = 48G
- • 效果：
- • 显存消耗：启动并运行后共占用20658MiB * 2 (gpu-memory-utilization 0.78 - 最大tokens 311,951)

选择模型



下载模型

使用modelscope

```bash
pip install modelscope
modelscope download --model cyankiwi/Qwen3.8-27B-AWQ-INT4 --local_dir ./Qwen3.8-27B-AWQ-INT4-cyankiwi
```

使用docker部署

> 在部署像 vLLM、SGLang 这类大模型推理引擎时，使用 Docker 主要有以下核心原因：
>
> 1. **解决复杂的依赖与环境冲突**
>    - 大模型推理工具对底层环境要求极高，通常依赖特定版本的 **Python、PyTorch、CUDA、cuDNN、Triton、NCCL** 等。
>    - 直接在宿主机（物理机）安装容易遇到版本不匹配等问题。Docker 将所有依赖打包在镜像中。
> 2. **极简的一键部署与跨平台一致性**
>    - 借助 `docker-compose.yml`，可以将模型路径、显卡分配、推理参数（如上下文长度、并行度等）全部通过配置文件固定下来。
> 3. **方便的 GPU 资源隔离与调度**
>    - 结合 NVIDIA Container Toolkit，可以非常精准地为容器指定显卡（如指定 `device_ids: ["0", "1"]` 运行张量并行）、设置共享内存（`shm_size: 32g`）和内存锁定限制（`ulimits`），防止不同服务抢占系统资源。

linux环境下docker清理

```bash
# 查看docker 信息
docker --version
which docker
systemctl status docker
docker info
```

```bash
# 清理 docker
docker system df					# 磁盘占用
docker images
docker system prune -f
docker ps -a


```

```bash
# 卸载 docker
sudo systemctl stop docker docker.socket containerd
sudo apt-get purge docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin docker-ce-rootless-extras
sudo rm -rf /var/lib/docker
```



```bash
# 安装 docker

# 指定镜像安装目录

```

```bash
# 一些配置

```

部署qwen3.8

docker-compose.yml

```yml
```

测试效果
