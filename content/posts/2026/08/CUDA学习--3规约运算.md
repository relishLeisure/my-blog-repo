---
title: "CUDA学习--3规约运算"
date: 2026-08-30T20:31:05+08:00
draft: true
slug: 
categories: [CUDA,笔记]
---



# 目录



[Reduction](https://leetgpu.com/challenges/reduction)

[Softmax](https://leetgpu.com/challenges/softmax)



Reduction

教程

[知乎文章--CUDA代码实战-reduce优化](https://zhuanlan.zhihu.com/p/7818317945)

LeetGPU

CUDA

while循环，在每个block 内做reduce

```c++
#include <cuda_runtime.h>

#define BLOCK_SIZE 256

// 每个 block 求reduce的sum，将结果存储到blockIdx对应的位置
__global__ void reduce_block_kernel(float* input, float* block_sum, int N) 
{
    // 每个线程的 id, 在每个 block 内部进行 reduce ，不需要全局id
    int tid = threadIdx.x;
    // 每个 block 第一个的 id
    int blockId = blockIdx.x * blockDim.x;
    // 全局id，global_id, thread 在数组中的位置
    int gid = blockId + tid;
    // 求和
    for (int offset = blockDim.x >> 1; offset > 0; offset >>= 1)
    {
        if (tid < offset)
        {
            if (gid + offset < N) {
                input[gid] += input[gid + offset];
            }
        }
        __syncthreads();
    }
    // 只有每个block第一个复制
    if(tid == 0){
        block_sum[blockIdx.x] = input[blockId];
    }
}

extern "C" void solve(const float* input, float* output, int N)
{
    float *cur_dev = nullptr;
    // 拷贝原始输入到可读写缓冲区（保护const只读输入）
    cudaMalloc(&cur_dev, sizeof(float)*N);
    cudaMemcpy(cur_dev, input, sizeof(float)*N, cudaMemcpyDeviceToDevice);

    int cur_N = N;
    float *tmp = nullptr;
    while(true)
    {
        int grid_size = (cur_N + BLOCK_SIZE - 1) / BLOCK_SIZE;
        cudaMalloc(&tmp, sizeof(float)*grid_size);

        reduce_block_kernel<<<grid_size, BLOCK_SIZE>>>(cur_dev, tmp, cur_N);
        cudaFree(cur_dev);
        cur_dev = tmp;
        cur_N = grid_size;

        if(cur_N == 1)
        {
            // cur_dev[0] 拷贝到 output[0]
            cudaMemcpy(output, cur_dev, sizeof(float), cudaMemcpyDeviceToDevice);
            cudaFree(cur_dev);
            break;
        }
    }
    cudaDeviceSynchronize();
}

```

共享内存优化

```c++
// 使用共享内存
__global__ void reduce_block_kernel(const float* input, float* block_sum, int N) 
{
    // 每个 block 内部 thread 的索引
    int tid = threadIdx.x;
    // 每个 block 第一个的 id
    int blockId = blockIdx.x * blockDim.x;
    // 使用共享内存
    __shared__ float f[BLOCK_SIZE];
    f[tid] = (blockId + tid) < N ? input[blockId + tid] : 0.0f;
    __syncthreads();														// 级同步
    // 求和
    for (int offset = blockDim.x >> 1; offset > 0; offset >>= 1)
    {
        if (tid < offset)
        {
            f[tid] += f[tid + offset];	
        }
        __syncthreads();													// 级同步
    }
    block_sum[blockIdx.x] = f[0];   
}
```



解决bank confilct

什么bank，什么是bank confilct?

首先，为了实现高带宽，共享内存被分为大小相等的内存模块(32个)，称为存储体(bank)，**可以同时访问**。因此，由落入*n 个*不同存储体的*n 个*地址发出的任何存储器读或写请求都可以同时得到服务，从而产生比单个模块的带宽高*n*倍的总带宽。





Softmax

PyTorch

```python
import numpy as np

def softmax(x):
    # 如果输入是一维向量，确保维度对齐
    # 针对二维数组（如包含多个样本的 batch 数据），在最后一个维度上求最大值并保持维度
    x_max = np.max(x, axis=-1, keepdims=True)
    
    # 减去最大值以防止上溢（减去常数不改变 softmax 的输出值）
    exp_x = np.exp(x - x_max)
    
    # 计算概率分布
    return exp_x / np.sum(exp_x, axis=-1, keepdims=True)

# 示例调用
x = np.array([2.0, 1.0, 0.1])
print(softmax(x))
# 输出: [0.65900114, 0.24243297, 0.09856589]
```

**CUDA**

需要三个核函数

1. 最大值
2. 求减去最大值的exp_sum
3. 除以exp_sum（归一化输出）



### **一维softmax简单版本**

```c++
#include <cuda_runtime.h>
#include <float.h>
#include <math.h>

// CUDA 原生不支持 float 的 atomicMax，这里使用 atomicCAS 实现线程安全的全局最大值更新
__device__ __forceinline__ float atomicMaxFloat(float* addr, float value) {
    float old = *addr, assumed;
    if(old >= value) return old;
    do {
        assumed = old;
        old = __int_as_float(atomicCAS((int*)addr, 
                                       __float_as_int(assumed), 
                                       __float_as_int(fmaxf(value, assumed))));
    } while (assumed != old);
    return old;
}

// kernel 1 : reduce_max : 寻找全局最大值
__global__ void reduce_max_kernel(const float* input, float* d_max, int N)
{
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    int stride = blockDim.x * gridDim.x; // Grid-Stride 步长
    
    // 每个线程处理多个元素（处理 N 大于 线程总数 的情况）
    for (int i = tid; i < N; i += stride) {
        // 直接使用原子操作更新全局最大值（最简单，但效率低于共享内存）
        atomicMaxFloat(d_max, input[i]);
    }
}

// kernel 2 : sum_exp : 计算 exp 并累加求和
__global__ void sum_exp_kernel(const float* input, float* output, float* d_max, float* d_sum, int N)
{
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    int stride = blockDim.x * gridDim.x;
    
    // 提前把全局最大值读到寄存器，避免在循环里重复读全局内存
    float max_val = *d_max; 

    for (int i = tid; i < N; i += stride) {
        // 注意：host端传入的 input 是 const，不能修改，所以把 exp 结果存入 output
        float exp_val = expf(input[i] - max_val);
        output[i] = exp_val; 
        
        // 多线程同时累加全局变量，必须使用原子操作(atomicAdd)
        atomicAdd(d_sum, exp_val);
    }
}

// kernel 3 : div : 计算最终的 softmax 概率
__global__ void div_kernel(float* output, float* d_sum, int N)
{
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    int stride = blockDim.x * gridDim.x;
    
    float sum_val = *d_sum;

    for (int i = tid; i < N; i += stride) {
        // 将第二步存在 output 里的 exp 值除以总和
        output[i] /= sum_val;
    }
}

// ==========================================
// Host 端调度逻辑
// ==========================================
extern "C" void solve(const float* input, float* output, int N) {
    // 1. 在 Device 端分配并初始化全局变量
    float *d_max, *d_sum;
    cudaMalloc(&d_max, sizeof(float));
    cudaMalloc(&d_sum, sizeof(float));

    float h_init_max = -FLT_MAX;
    float h_init_sum = 0.0f;
    cudaMemcpy(d_max, &h_init_max, sizeof(float), cudaMemcpyHostToDevice);
    cudaMemcpy(d_sum, &h_init_sum, sizeof(float), cudaMemcpyHostToDevice);

    // 2. 线程与网格配置
    int threads = 256;
    // 限制最大 Block 数量，利用 Grid-Stride Loop 处理任意长度 N
    int blocks = (N + threads - 1) / threads;
    blocks = blocks > 1024 ? 1024 : blocks; 

    // 3. 依次启动三个 Kernel
    reduce_max_kernel<<<blocks, threads>>>(input, d_max, N);
    sum_exp_kernel<<<blocks, threads>>>(input, output, d_max, d_sum, N);
    
    // 第三步只需 output 和 d_sum
    div_kernel<<<blocks, threads>>>(output, d_sum, N);

    cudaDeviceSynchronize();

    // 4. 清理内存
    cudaFree(d_max);
    cudaFree(d_sum);
}
```

**Grid-Stride**

Grid-Stride的作用：限制最大 Block 数量，如果block过多，就进入下一个grid

```c++
int grid_stride = blockDim.x * gridDim.x; // Grid-Stride 步长，表示 grid x轴方向上的长度，一维数据下等于跨grid访问的步长
// 二维 (rows,cols)
int stride_x = blockDim.x * gridDim.x;	  // 行列各自跨步
int stride_y = blockDim.y * gridDim.y;
int grid_stride = stride_x * stride_y;	  // 只有在数据是数组存储
```

限制最大 Block 数量:  不合理的大量 Block 会带来性能下降、资源浪费，极端情况触发调度 / 内存开销问题；真正的瓶颈是硬件调度、资源占用、负载均衡。

> 好像明白了 ，grid_stride 是限制了线程的数量，这些线程分批处理input数据，就像机械手一样，分批并行处理工厂流水线上的任务

**对比下面两个版本的block数量**

```c++
// 简单版本
__global__ void reduce_max_kernel_1(const float* input, float* d_max, int N)
{
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid < N) {
        atomicMaxFloat(d_max, input[tid]);
    }
}

// Grid-Stride  版本
__global__ void reduce_max_kernel_2(const float* input, float* d_max, int N)
{
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    int stride = blockDim.x * gridDim.x; 
    for (int i = tid; i < N; i += stride) {
        atomicMaxFloat(d_max, input[i]);
    }
}
```

**参数的形状**

```c++
// kernel<<<gridDim, blockDim>>>(...);    指定 grid 和 block 切分的尺寸，至少有一个 block 一个 grid，如果数据量比较多会根据形状计算
kernel<<<blocks, threads>>>(...);
```



### 二维softmax简单版本







