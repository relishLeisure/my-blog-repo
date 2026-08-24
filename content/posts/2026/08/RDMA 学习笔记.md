---
title: "RDMA 学习笔记"
date: 2026-08-24T17:38:02+08:00
draft: false
slug: 
categories: [RDMA,笔记]
---

# 术语

**NIC** : Network Interface Card, 网络适配器 / 网卡。 **解释：** 连接计算机与网络的硬件组件。在 AI 数据中心，普通 NIC 已无法满足需求，通常需要支持高吞吐和低延迟协议（如 RoCE）的专用高性能网卡。

**SmartNIC / DPU** : Smart Network Interface Card / Data Processing Unit, 智能网卡 / 数据处理器。 **解释：** 带有独立处理器的网卡。它能卸载原本由 CPU 处理的网络、存储和安全任务，让昂贵的计算资源完全服务于 AI 模型。

**RDMA** : Remote Direct Memory Access, 远程直接内存访问。 **解释：** 允许计算机直接访问远程内存的技术，绕过操作系统内核和 CPU 干扰。它是实现多 GPU 集群超低延迟通信的底层基石。

**RoCE** : RDMA over Converged Ethernet, 基于融合以太网的 RDMA。 **解释：** 在标准以太网上运行 RDMA 的协议。它让数据中心能在不更换昂贵专用网络设备的前提下，获得接近无限带宽技术的传输性能。

**NCCL** : NVIDIA Collective Communications Library, 英伟达集合通信库。 **解释：** 专门优化英伟达 GPU 间数据交换的算法库。它定义了多卡如何高效同步数据，是分布式训练的“通信翻译官”。

**K8s (Kubernetes)** : Kubernetes, 容器编排平台。 **解释：** AI 云平台的“大脑”。负责自动调度算力任务、管理容器化应用，并对 GPU 硬件资源进行统一分配与回收。

**SDN** : Software Defined Networking, 软件定义网络。 **解释：** 将网络控制权收归软件的技术。允许 AI 平台像调配内存一样，通过代码动态调节网络带宽和路径，提升集群灵活性。

**InfiniBand (IB)** : InfiniBand, 无限带宽技术。 **解释：** 一种专为高性能计算设计的互联标准。提供物理层级的极低延迟和极高带宽，常用于顶级大模型训练集群。

**VPC** : Virtual Private Cloud, 虚拟私有云。 **解释：** 在公有云中为用户划分的私有网络区域。通过逻辑隔离，保证不同租户的 AI 训练数据和算力环境互不干扰。

RDMA本身指的是一种技术，具体协议层面，包含[Infiniband](https://zhida.zhihu.com/search?content_id=118992942&content_type=Article&match_order=1&q=Infiniband&zhida_source=entity)（IB），RDMA over Converged Ethernet（RoCE）和internet Wide Area RDMA Protocol（iWARP）。

# 某岗位信息

### 岗位关联小结

- KVM/QEMU/Xen：**底层虚拟机虚拟化**，DPU 智能网卡需适配虚拟网络、硬件直通；
- OpenStack：**云集群管控**，对应大规模云环境测试场景；
- Docker：**容器虚拟化**，云原生业务场景，也是 DPU 当下重点适配的云化场景。

职位要求

1.全栈技术测试：涵盖GPU驱动层、AI编译器、高性能算子库、深度学习框架，工具链等AI技术栈的质量保障工作；

2.稳定性与兼容性验证：验证系统在大模型场景下的稳定性，确保各组件功能正确性和跨平台兼容性；

3.测试用例设计与执行：设计覆盖各类边界条件和异常场景的测试用例，确保功能正确性和系统稳定性；

4.性能分析与优化：使用专业工具进行性能瓶颈分析，输出数据驱动的优化建议和性能趋势报告；

5.精度验证与对比：验证各种数据类型下的数值精度，对比不同版本间的功能和性能差异；

6.自动化开发：使用Python（pytest）/ GoogleTest开发自动化测试脚本，集成CI流水线；

7.问题定位与分析：通过日志分析工具（GDB/Valgrind/Profiling）进行问题复现，精准定位缺陷根因；

8.工具开发：参与测试工具开发（自动化测试数据生成脚本库等），提升测试效率。

# 优秀作者知乎文章索引

[《RDMA杂谈》专栏索引](https://zhuanlan.zhihu.com/p/164908617)

# 学习笔记

上述知乎文章的学习笔记

## 一 RDMA 概念篇

### 1. RDMA概述

RDMA

DMA，传统网卡发送接收数据需要经过CPU，非常耗时，而且还需要linux切换内核态和用户态

0拷贝：不需要在用户空间和内核空间中来回复制数据

内核Bypass：IO（数据）流程可以绕过内核，即在用户层就可以把数据准备好并通知硬件准备发送和接收。避免了系统调用和上下文切换的开销。

CPU卸载：指的是可以在远端节点CPU不参与通信的情况下（当然要持有访问远端某段内存的“钥匙”才行）对内存进行读写

协议：RDMA的具体实现

[Infiniband](https://zhida.zhihu.com/search?content_id=118992942&content_type=Article&match_order=1&q=Infiniband&zhida_source=entity)（IB），RDMA over Converged Ethernet（RoCE）和internet Wide Area RDMA Protocol（iWARP）

### 2. 比较基于传统以太网与RDMA技术的通信

RDMA的分层模型分成两部分“控制通路”和“数据通路”，控制通路需要进入内核态准备通信所需的内存资源，而数据通路指的是实际数据交互过程中的流程。

![img](https://pica.zhimg.com/v2-8ef2b015ba9d111fc2d42983cd5fe152_1440w.jpg)

### 3 RDMA基本元素

![img](https://pic3.zhimg.com/v2-b6723caa5b291ee161d94fd8fd8ce09c_1440w.jpg)

WQ，Work Queue  软件给硬件的任务队列，WQE, Work Queue Element

RDMA技术中**通信的基本单元是QP**, QP Queue  Pair  一对 WQ, 也就是发送和接收。SQ, Send Queue ； RQ, Receive Queue 

QPN（Queue Pair Number）,QP 的唯一编号

Shared Receive Queue简称SRQ，意为共享接收队列。多个SQ共享一个RQ，节省内存

Completion Queue简称CQ，意为完成队列

![img](https://pic2.zhimg.com/v2-a8d38721903672037b27cc7e49ecee03_1440w.jpg)

WR全称为Work Request，意为工作请求；WC全称Work Completion，意为工作完成。这两者其实是WQE和CQE在用户层的“映射”。

[1]《IB Specification Vol 1-Release-1.3-2015-03-03》

### [4. RDMA操作类型](https://zhuanlan.zhihu.com/p/142175657)

#### SEND & RECV

#### READ & WRITE***  

看原帖，图画的非常好

个人想法> 我们不生产数据，我们只是数据的搬运工，CV工程师

**[1] part1-OFA_Training_Sept_2016.pdf** 是**2016 年 9 月发布的 OFA（OpenFabrics Alliance，开放架构联盟）官方培训资料第一部分**，是 RDMA（远程直接内存访问）领域的经典入门 / 培训文档。

### [5. RDMA基本服务类型](https://zhuanlan.zhihu.com/p/144099636)

[IB协议](https://zhida.zhihu.com/search?content_id=120154436&content_type=Article&match_order=1&q=IB协议&zhida_source=entity)中通过“可靠”和“连接”两个维度来描述一种服务类型。

#### 可靠/不可靠

可靠需要保证数据**无损和有序**

三个机制来保证可靠性：ACK,数据校验，保序性

#### 连接与数据报（Datagram）



### 服务类型

|                    | 可靠（Reliable）          | 不可靠 (Unreliable)         |
| ------------------ | ------------------------- | --------------------------- |
| 连接（Connection） | RC（Reliable Connection） | UC（Unreliable Connection） |
| 数据报（Datagram） | RD（Reliable Datagram）   | UD（Unreliable Datagram）   |

RC和[UD](https://zhida.zhihu.com/search?content_id=120154436&content_type=Article&match_order=1&q=UD&zhida_source=entity)是应用最多的两种，可以类比成TCP和UDP。

### [6. RDMA之Memory Region](https://zhuanlan.zhihu.com/p/156975042)

## MR，Memory Region

#### 地址映射

1.为保证安全，防止软件读取关键物理地址Phisical Address，

**MMU 全称：内存管理单元（Memory Management Unit）**，用于虚拟地址与物理地址的映射

IB协议中，用户在申请完用于存放数据的内存区域之后，都需要通过调用IB框架提供的API注册MR，才能让RDMA网卡访问这片内存区域。

我们通常称RDMA硬件为**[HCA](https://zhida.zhihu.com/search?content_id=123016342&content_type=Article&match_order=1&q=HCA&zhida_source=entity)（Host Channel Adapter， 宿主通道适配器）**

#### 权限控制

#### 避免换页

换页：内存为分页存储/读取，操作系统为提高内存使用效率，会将使用频率低的内存搬运。影响VA-PA的映射关系

### [7. RDMA之Protection Domain](https://zhuanlan.zhihu.com/p/159493100)

PD, Protection Domain, 包括 QP 和 MR，（工作队列对 和 内存区域），就像分组一样

### [8. RDMA之Address Handle](https://zhuanlan.zhihu.com/p/163552044)

IB协议中的这个标识被称为GID（Global Identifier，全局ID）**，是一个128 bits的序列。

AH全称为Address Handle，理解为一组定位节点和存储地址的句柄，并且对用户隐藏信息

### [9. RDMA之Queue Pair](https://zhuanlan.zhihu.com/p/195757767)

QPC全称是Queue Pair Context，用于存储QP相关属性。如SQ Address, RQ Address, SQ size等

QP Number， QPN， 编号

QP 状态机

### 10 RDMA之Completion Queue

WQ和CQ的对应关系——每个WQ都必须关联一个CQ，而每个CQ可以关联多个SQ和RQ。

CQE

CQC: （Completion Queue Context），存储CQ对应的详细信息的一段内存结构。

CQN: CQ Number

#### 完成错误

[IB协议](https://zhida.zhihu.com/search?content_id=145830961&content_type=Article&match_order=1&q=IB协议&zhida_source=entity)中有三种错误类型，立即错误（immediate error）、完成错误（Completion Error）以及异步错误（Asynchronous Errors)。

立即错误的是“立即停止当前操作，并返回错误给上层用户”；

完成错误指的是“通过CQE将错误信息返回给上层用户”；

异步错误指的是“通过中断事件的方式上报给上层用户”。

### [11. RDMA之Shared Receive Queue](https://zhuanlan.zhihu.com/p/279904125)

#### 为什么

为什么要用SRQ？SQ中下发任务的数量要远远超过向RQ中下发任务的数量，这是因为

SEND/WRITE/READ都需要通信发起方向SQ中下发一个WR，而只有和SEND配合的RECV操作才需要通信响应方下发WR到RQ中（带立即数的Write操作也会消耗Receive WR，我们还没讲到）。

![img](https://pica.zhimg.com/v2-7aa714891aa161db06800440c64d01da_1440w.jpg)

sge（Scatter/Gather Element）组成的，每个sge由一个内存地址，长度和秘钥组成。sge指向一块连续的内存区域；

多个sge就可以表示多个彼此离散的连续内存块，我们称多个sge为sgl（Scatter/Gather List）。

#### 异步事件

SRQ有一个特殊的异步事件，用来及时通知上层用户SRQ的状态，即SRQ Limit Reached事件。

SRQ Limit：SRQ可以设置一个水线/阈值，当队列中剩余的WQE数量小于水线时，这个SRQ会就上报一个异步事件。提醒用户“队列中的WQE快用完了，请下发更多WQE以防没有地方接收新的数据”。这个水线/阈值就被称为SRQ Limit，这个上报的事件就被称为SRQ Limit Reached。

“我这里空间挺大的（小于limit），快多放些东西在我这吧，免得货物太多了”

#### 用户接口

### [12 RDMA之Memory Window](https://zhuanlan.zhihu.com/p/353590347)***

Memory Window 由用户申请的，用于让远端节点访问本端内存区域的RDMA资源。

#### MR/MW的权限配置

|        |    本端     |     对端     |
| :----: | :---------: | :----------: |
| **读** | Local Read  | Remote Read  |
| **写** | Local Write | Remote Write |

#### Memory Key

一块内存区域的标识；Key是一串数字，由两部分组成：24bit的Index以及8bit的Key：Index用于映射MR，key校验整个字段的合法性。

一块内存区域有 Local Key和Remote Key 两种（都有），Local Key和Remote Key：

L_Key: 本地HCA会校验传递的L_Key。并且利用L_Key中的索引查找地址转换表，把虚拟地址翻译成物理地址然后访问内存。

R_Key: 类似，只是本地HCA提供给远端HCA的访问标识，

#### 为什么要有MW

[Memory Region](https://zhuanlan.zhihu.com/p/156975042)一文中介绍过用户注册MR的过程，需要从用户态陷入内核态

**MW在创建好之后，可以通过数据路径（即通过用户态直接下发WR到硬件的方式）动态的绑定到一个已经注册的MR上，并同时设置或者更改其访问权限，这个过程的速度远远超过重新注册MR的过程。**

这里内容很多——跳过了***

## 二 RDMA软件栈篇

TODO

### [1 3RDMA之Verbs](https://zhuanlan.zhihu.com/p/329198771)

[14RDMA之用户态与内核态交互](https://zhuanlan.zhihu.com/p/346708569)

### 15. RDMA之RoCE & Soft-RoCE

#### RoCE

RoCE全称是RDMA over Converged Ethernet，即基于融合以太网的RDMA。用通俗的话讲，就是基于传统以太网的部分下层协议，在其基础上实现Infiniband的部分上层协议。这里的RoCE特指RoCE v2;

### RoCE层次

![img](https://pic3.zhimg.com/v2-17e04efb14c550ad0be456b7b71209b4_1440w.jpg)

#### RoCE协议的优势

RoCE v2协议的出现解决了这一问题，如果用户想要从以太网切换到RoCE，那么只需要购买支持RoCE的网卡就可以了，线缆、交换机和路由器（RoCE v1不支持以太网路由器）等网络设备都是兼容的——因为我们只是在以太网传输层基础上又定义了一套协议而已。

#### Soft-RoCE

RXE（Software RDMA over Ethernet, Soft-RoCE）是 RoCEv2 的软件实现，Linux内核模块名 `rdma_rxe`，让普通以太网卡也能跑 RDMA 应用。

### 16 Pyverbs（Python Verbs）

### 17内存地址基础知识

#### 18Queue Buffer

### 19用户态Memory Region Buffer

# 相关技术

RMDA/RoCE v2/DPDK

UVX (UCloud Virtual eXchange)

KVM 底层虚拟机虚拟化

## 









