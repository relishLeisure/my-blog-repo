---
title: "CUDA学习--1加法"
date: 2026-08-27T15:58:05+08:00
draft: true
slug: "CUDA"
categories: [CUDA,笔记]
---



**文件位置**

https://github.com/Tony-Tan/CUDA_Freshman

# 加法代码

## 1代码结构

这段代码很好地说明了结构

```c++
/*
* https://github.com/Tony-Tan/CUDA_Freshman
* 3_sum_arrays
*/
#include <cuda_runtime.h>
#include <stdio.h>
#include "freshman.h"

// cpu 流水线 计算向量之和
void sumArrays(float * a,float * b,float * res,const int size)
{
    for(int i=0;i<size;i+=4)
    {
        res[i]=a[i]+b[i];
        res[i+1]=a[i+1]+b[i+1];
        res[i+2]=a[i+2]+b[i+2];
        res[i+3]=a[i+3]+b[i+3];
	}
}
// gpu 计算向量之和，每个线程并行执行，根据自己所处的位置（id）执行不同的操作
__global__ void sumArraysGPU(float*a,float*b,float*res)
{
    int i=threadIdx.x;
    res[i]=a[i]+b[i];
}
// main 函数，程序的入口
int main(int argc,char **argv)
{
    // cuda 设备
    int dev = 0;
    cudaSetDevice(dev);									
    // 尺寸计算
    int nElem=32;
    printf("Vector size:%d\n",nElem);
    int nByte=sizeof(float)*nElem;
    // cpu分配内存
    float *a_h=(float*)malloc(nByte);
    float *b_h=(float*)malloc(nByte);
    float *res_h=(float*)malloc(nByte);
    float *res_from_gpu_h=(float*)malloc(nByte);
    memset(res_h,0,nByte);
    memset(res_from_gpu_h,0,nByte);
    // 检查gpu内存分配
    float *a_d,*b_d,*res_d;
    CHECK(cudaMalloc((float**)&a_d,nByte));
    CHECK(cudaMalloc((float**)&b_d,nByte));
    CHECK(cudaMalloc((float**)&res_d,nByte));
    // cpu内存数据：初始化赋值
    initialData(a_h,nElem);
    initialData(b_h,nElem);
    // 数据从cpu/host拷贝到gpu/device
    CHECK(cudaMemcpy(a_d,a_h,nByte,cudaMemcpyHostToDevice));
    CHECK(cudaMemcpy(b_d,b_h,nByte,cudaMemcpyHostToDevice));
    // 核函数
    dim3 block(nElem);
    dim3 grid(nElem/block.x);
    sumArraysGPU<<<grid,block>>>(a_d,b_d,res_d);
    printf("Execution configuration<<<%d,%d>>>\n",block.x,grid.x);
    // 数据从device拷贝到host
    CHECK(cudaMemcpy(res_from_gpu_h,res_d,nByte,cudaMemcpyDeviceToHost));
    sumArrays(a_h,b_h,res_h,nElem);
    // 核验计算结果
    checkResult(res_h,res_from_gpu_h,nElem);
    // 释放cuda内存
    cudaFree(a_d);
    cudaFree(b_d);
    cudaFree(res_d);
    // 释放cpu内存
    free(a_h);
    free(b_h);
    free(res_h);
    free(res_from_gpu_h);

    return 0;
}
```

## **2线程管理**

上面代码的核函数出现`<<<grid,block>>>`

```c++
// 核函数
dim3 block(nElem);									// 
dim3 grid(nElem/block.x);
sumArraysGPU<<<grid,block>>>(a_d,b_d,res_d);
```

- 1个kernel 对应 1个grid
- 1个grid对应多个block 
- 1个block里面有多个线程（每个block里的thread数量是32的整数倍）

**形象化————复述**

- 每个Grid是一个大厂房
- 每个Block是一个车间，整齐排布在Grid中
- 每个Thread是一个工人，以 32 为一组，每个Block中的工人数量都是 32 的整数倍，最少 32 个，最多 1024 个线程。
- 每个Block中的线程同步，共享内存

**线程标号**

区分线程拿到不同数据
- blockIdx（block 在 grid 中的位置索引）
- threadIdx（thread 在 block 中的位置索引）

- blockIdx.x    blockIdx.y    blockIdx.z    
- threadIdx.x   threadIdx.y   threadIdx.z

**标号的方向**

```txt
00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15         --> x 
|
| y
V 

[         ] [         ] [         ] [         ]    
[00 01 02 03]                                        blockDim:(4,1,1)
   	                                                 threadIdx:  thread 位于 grid 的位置索引
[[ block0 ] [ block1 ]] 					       gridDim:(2,2,1)				
[[ block2 ] [ block3 ]] 	     				   blockIdx: block 位于 grid 的位置索引



```

**线程的全局索引**

线程的全局索引 == 数据在数组中的索引 == 指针指向内存空间的偏置
一维数组

```c++
int tid = blockIdx.x * blockDim.x + threadIdx.x;  
```
二维矩阵
```c++
// 内核内
int x = blockIdx.x * blockDim.x + threadIdx.x; // 全局列号
int y = blockIdx.y * blockDim.y + threadIdx.y; // 全局行号
if (x < W && y < H) { // W=总列数(宽度)，H=总行数(高度)
    int tid = y * W + x; // 行优先转线性索引
    C[tid] = A[tid] + B[tid];
}
```
三维张量
```c++
// 内核内
int x = blockIdx.x * blockDim.x + threadIdx.x; // 列
int y = blockIdx.y * blockDim.y + threadIdx.y; // 行
int z = blockIdx.z * blockDim.z + threadIdx.z; // 深度/批次

if (x < W && y < H && z < D) { // W=宽, H=高, D=深度
    int tid = z * (H * W) + y * W + x; // 三维转线性索引
    C[tid] = A[tid] + B[tid];
}
```

## **3维度表示**

注意：这里是一维排布！

```c++
// 1. 每个 Block 里的线程数量
dim3 block(256);  							

// 2. 设置 Grid 里需要多少个 Block
// 计算方式：总数据量 / 每个 Block 的容量。
// (通常写成 (nElem + block.x - 1) / block.x 向上取整，防止除不尽)
dim3 grid(nElem / block.x); 				

// 3. 启动内核函数（Kernel Launch）
sumArraysGPU<<<grid, block>>>(a_d, b_d, res_d);
```

二维写法（仍然表示一维）

```c++
// 1. 每个 Block 里的线程数量
dim3 block(256,1);  							

// 2. 设置 Grid 里需要多少个 Block
// (通常写成 (nElem + block.x - 1) / block.x 向上取整，防止除不尽)
dim3 grid((nElem + block.x - 1) / block.x, 1); 				

// 3. 启动内核函数（Kernel Launch）
sumArraysGPU<<<grid, block>>>(a_d, b_d, res_d);
```

**核函数**

```c++
int tid = blockIdx.x * blockDim.x + threadIdx.x;
```

```c++
__global__ void sumArraysGPU(float*a,float*b,float*res)
{
    int i=threadIdx.x;		// 在这个场景中，一维向量加法，线程id就等于数组的索引，因为blockIdx.x等于0
    res[i]=a[i]+b[i];
}
```

## **4在LeetGPU上刷一道向量加法**

https://leetgpu.com/challenges/vector-addition

> int 范围 32位
>
> - 最大值：`2^31 - 1 = 2147483647`
> - 最小值：`-2^31 = -2147483648`

CUDA

```c++
#include <cuda_runtime.h>

__global__ void vector_add(const float* A, const float* B, float* C, int N) {
    int id = blockIdx.x * blockDim.x + threadIdx.x;
    if (id < N) {
        C[id] = A[id] + B[id];
    }
}

// A, B, C are device pointers (i.e. pointers to memory on the GPU)
extern "C" void solve(const float* A, const float* B, float* C, int N) {
    int threadsPerBlock = 256;
    int blocksPerGrid = (N + threadsPerBlock - 1) / threadsPerBlock;

    vector_add<<<blocksPerGrid, threadsPerBlock>>>(A, B, C, N);
    cudaDeviceSynchronize();
}
```

Triton

```python
import torch
import triton
import triton.language as tl


@triton.jit
def vector_add_kernel(a, b, c, n_elements, BLOCK_SIZE: tl.constexpr):
    # 1. 获取当前 Block (Program) 的 ID
    pid = tl.program_id(axis=0)
    
    # 2. 计算当前 Block 需要处理的全局索引 (offsets)
    # tl.arange(0, BLOCK_SIZE) 生成 [0, 1, ..., BLOCK_SIZE-1]
    block_start = pid * BLOCK_SIZE
    offsets = block_start + tl.arange(0, BLOCK_SIZE)
    
    # 3. 边界保护，防止最后一个 Block 越界
    mask = offsets < n_elements
    
    # 4. 加载数据
    # 注意：这里的 a 和 b 实际上是显存指针，a + offsets 得到一批地址
    x = tl.load(a + offsets, mask=mask)
    y = tl.load(b + offsets, mask=mask)
    
    # 5. 执行加法并写回显存
    # 这里用 x + y，避免覆盖传进来的同名变量 a 和 b
    tl.store(c + offsets, x + y, mask=mask)


# a, b, c are tensors on the GPU
def solve(a: torch.Tensor, b: torch.Tensor, c: torch.Tensor, N: int):
    BLOCK_SIZE = 1024
    grid = (triton.cdiv(N, BLOCK_SIZE),)					# N 分配的内存空间，BLOCK_SIZE block的尺寸
    vector_add_kernel[grid](a, b, c, N, BLOCK_SIZE)

```

## 5矩阵加法

CUDA

```c++
#include <cuda_runtime.h>

// 解法1：二维矩阵坐标
__global__ void matrix_add_2d(const float* A, const float* B, float* C, int N) {
    int x = blockIdx.x * blockDim.x + threadIdx.x;
    int y = blockIdx.y * blockDim.y + threadIdx.y;
    int tid = y * gridDim.x + x;
    if (x < N && y < N) {
        C[tid] = A[tid] + B[tid];
    }
}

// 解法2：在内存空间中，实际上本来就是一维矩阵
__global__ void matrix_add_1d(const float* A, const float* B, float* C, int N) {
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid < N * N) {
        C[tid] = A[tid] + B[tid];
    }
}

// A, B, C are device pointers (i.e. pointers to memory on the GPU)
extern "C" void solve(const float* A, const float* B, float* C, int N) {
    int threadsPerBlock = 256;
    int blocksPerGrid = (N * N + threadsPerBlock - 1) / threadsPerBlock;
    // 一维的 grid/block 配置
    matrix_add<<<blocksPerGrid, threadsPerBlock>>>(A, B, C, N);
    cudaDeviceSynchronize();
}
```

Triton

```python
import torch
import triton
import triton.language as tl

# 代码和向量加法完全一样
@triton.jit
def matrix_add_kernel(a, b, c, n_elements, BLOCK_SIZE: tl.constexpr):
    pid = tl.program_id(axis=0)
    block_start = pid * BLOCK_SIZE
    offsets = block_start + tl.arange(0, BLOCK_SIZE)
    mask = offsets < n_elements
    x = tl.load(a + offsets, mask=mask)
    y = tl.load(b + offsets, mask=mask)
    tl.store(c + offsets, x + y, mask=mask)


# a, b, c are tensors on the GPU
def solve(a: torch.Tensor, b: torch.Tensor, c: torch.Tensor, N: int):
    BLOCK_SIZE = 1024
    n_elements = N * N
    grid = (triton.cdiv(n_elements, BLOCK_SIZE),)
    matrix_add_kernel[grid](a, b, c, n_elements, BLOCK_SIZE)
```



