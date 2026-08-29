---
title: "CUDA学习--2简单运算"
date: 2026-08-28T16:00:05+08:00
draft: false
slug: 
categories: [CUDA,笔记]
---



# 目录

[1D Convolution](https://leetgpu.com/challenges/1d-convolution)

[Leaky ReLU](https://leetgpu.com/challenges/leaky-relu)

[Sigmoid Linear Unit](https://leetgpu.com/challenges/sigmoid-linear-unit)

[Matrix Transpose](https://leetgpu.com/challenges/matrix-transpose)

[Swish-Gated Linear Unit](https://leetgpu.com/challenges/swish-gated-linear-unit)

## 1D Convolution

CUDA

```c++
#include <cuda_runtime.h>

__global__ void convolution_1d_kernel(const float* input, const float* kernel, float* output,
                                      int input_size, int kernel_size) {
    int tid = blockIdx.x * blockDim.x + threadIdx.x; 
    float sum = 0.0f;
    if (tid < input_size - kernel_size + 1) {
        for (int i=0; i<kernel_size; ++i) {
            sum += input[tid + i] * kernel[i];
        }
        output[tid] = sum;
    }
}

// input, kernel, output are device pointers (i.e. pointers to memory on the GPU)
extern "C" void solve(const float* input, const float* kernel, float* output, int input_size,
                      int kernel_size) {
    int output_size = input_size - kernel_size + 1;
    int threadsPerBlock = 256;
    int blocksPerGrid = (output_size + threadsPerBlock - 1) / threadsPerBlock;

    convolution_1d_kernel<<<blocksPerGrid, threadsPerBlock>>>(input, kernel, output, input_size,
                                                              kernel_size);
    cudaDeviceSynchronize();
}

```

Triton

```python
import torch
import triton
import triton.language as tl


@triton.jit
def conv1d_kernel(input, kernel, output, input_size, kernel_size, BLOCK_SIZE: tl.constexpr):
    
    pass


# input, kernel, output are tensors on the GPU
def solve(
    input: torch.Tensor,
    kernel: torch.Tensor,
    output: torch.Tensor,
    input_size: int,
    kernel_size: int,
):
    BLOCK_SIZE = 1024
    n_blocks = triton.cdiv(input_size - kernel_size + 1, BLOCK_SIZE)
    grid = (n_blocks,)

    conv1d_kernel[grid](input, kernel, output, input_size, kernel_size, BLOCK_SIZE)

```

## Leaky ReLU

CUDA

```C++
#include <cuda_runtime.h>

__global__ void leaky_relu_kernel(const float* input, float* output, int N) {
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    float value = input[tid];
    if (tid < N) {
        if (value > 0) {
            output[tid] = value;
        }
        else {
            output[tid] = 0.01f * value;
        }
    }
}

// input, output are device pointers (i.e. pointers to memory on the GPU)
extern "C" void solve(const float* input, float* output, int N) {
    int threadsPerBlock = 256;
    int blocksPerGrid = (N + threadsPerBlock - 1) / threadsPerBlock;

    leaky_relu_kernel<<<blocksPerGrid, threadsPerBlock>>>(input, output, N);
    cudaDeviceSynchronize();
}
```

Triton

```python
@triton.jit
def leaky_relu_kernel(input, output, n_elements, BLOCK_SIZE: tl.constexpr):
    pass


# input, output are tensors on the GPU
def solve(input: torch.Tensor, output: torch.Tensor, N: int):
    BLOCK_SIZE = 1024
    grid = (triton.cdiv(N, BLOCK_SIZE),)
    leaky_relu_kernel[grid](input, output, N, BLOCK_SIZE)
```

## Sigmoid Linear Unit

CUDA

```c++
#include <cuda_runtime.h>

__global__ void silu_kernel(const float* input, float* output, int N) {
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    float value = input[tid];
    if (tid < N) {
        output[tid] = value / (1 + exp(- value));
    }
}

// input, output are device pointers
extern "C" void solve(const float* input, float* output, int N) {
    int threadsPerBlock = 256;
    int blocksPerGrid = (N + threadsPerBlock - 1) / threadsPerBlock;

    silu_kernel<<<blocksPerGrid, threadsPerBlock>>>(input, output, N);
    cudaDeviceSynchronize();
}
```

Triton

```python
```

## Matrix Transpose

CUDA

```C++
#include <cuda_runtime.h>

__global__ void matrix_transpose_kernel(const float* input, float* output, int rows, int cols) {
    int x = blockIdx.x * blockDim.x + threadIdx.x;
    int y = blockIdx.y * blockDim.y + threadIdx.y;
    if (y < rows && x < cols) {
        // input[row, col] 放到 output[col, row]
        int input_idx = y * cols + x;
        int output_idx = x * rows + y;
        output[output_idx] = input[input_idx];
    }
}

// input, output are device pointers (i.e. pointers to memory on the GPU)
extern "C" void solve(const float* input, float* output, int rows, int cols) {
    dim3 threadsPerBlock(16, 16);
    dim3 blocksPerGrid((cols + threadsPerBlock.x - 1) / threadsPerBlock.x,
                       (rows + threadsPerBlock.y - 1) / threadsPerBlock.y);

    matrix_transpose_kernel<<<blocksPerGrid, threadsPerBlock>>>(input, output, rows, cols);
    cudaDeviceSynchronize();
}

```

用到了 `dim3` 

## 一个很好的平台

刷题格式

```c++
#include <stdint.h>
#include <cuda_bf16.h>

// ReLU逐元素核函数：y = max(x, 0)
__global__ void relu_kernel(const __nv_bfloat16* x, __nv_bfloat16* y, int64_t total) {
    int64_t tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid < total) {
        // 转float计算再转回bf16，兼容性最好、逻辑最清晰
        // 使用 <cuda_bf16.h> 库函数实现 float <-> bf16 转换
        float val = __bfloat162float(x[tid]);
        val = val > 0.0f ? val : 0.0f;
        y[tid] = __float2bfloat16(val);
    }
}

/**
 * @param x    input
 * @param y    output
 * @param T,H    张量形状 (T,H)
 */
extern "C" void run_kernel(
    const __nv_bfloat16* x,
    __nv_bfloat16* y,
    int64_t T,
    int64_t H
) {
    int64_t total_elements = T * H;
    const int block_size = 256;
    int64_t grid_size = (total_elements + block_size - 1) / block_size;
    
    relu_kernel<<<grid_size, block_size>>>(x, y, total_elements);
    // cudaDeviceSynchronize();
}
```





## Swish-Gated Linear Unit

SWiGLU is defined as:

1. Split input into two halves: `x1` and `x2` 
2. silu(x1) = x1 / (1 + exp(- x1))
3. res = silu(x1) * x2

CUDA

```c++
#include <cuda_runtime.h>

__global__ void swiglu_kernel(const float* input, float* output, int halfN) {
    for (int i=0; i<halfN; ++i) {
        float silu = input[i] / (1 + exp(-input[i]));
        output[i] = silu * input[i+halfN];
    }
}

// input, output are device pointers
extern "C" void solve(const float* input, float* output, int N) {
    int halfN = N / 2;
    int threadsPerBlock = 256;
    int blocksPerGrid = (halfN + threadsPerBlock - 1) / threadsPerBlock;

    swiglu_kernel<<<blocksPerGrid, threadsPerBlock>>>(input, output, halfN);
    cudaDeviceSynchronize();
}
```

















