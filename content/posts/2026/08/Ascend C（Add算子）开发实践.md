---
title: "Ascend C（Add算子）开发实践"
date: 2026-08-27T20:53:02+08:00
draft: false
slug: 
categories: [CANN,实验]
---

| 实验名称 | Ascend C简单Vector算子开发实践（Add算子）                    |
| -------- | ------------------------------------------------------------ |
| 实验内容 | Add算子                                                      |
| 实验时间 | 2026-08-27                                                   |
| 实验类型 |                                                              |
| 实验地点 |                                                              |
| 在线地点 | https://www.hiascend.com/edu/experiment/detail/1d0b0b790fb24947977d6d954112c016?tab=1 |

# 环境与器材

**环境搭建**

本实验依赖基础NPU环境，包括昇腾NPU驱动、固件、Toolkit（CANN开发套件）、ops（CANN算子包集成一系列库文件 ）、**msprof性能采集工具**（随 CANN Toolkit 一起安装）。

**实验平台**

CANNLAB

https://gitcode.com/org/cann/cannlab/environment

# 实验过程

## 实验环境

1.启动环境

https://gitcode.com/org/cann/cannlab/environment/create

```txt
实例名称
cann_dev_env
名称可包含数字、字母、下划线，不能以数字开头，长度不超过15个字符。

模板名称
cann_8.5.2-py3.11-A2-arm

NPU规格
1*NPU 910B3 16vCPUs 32GiB
```

**notebook**

由于没有上面的npu资源了，换成使用notebook

cann 版本是8.5.0

https://gitcode.com/user/qq_4277658311111111111111173q/notebook/lab

2.**查看环境版本**

```bash
echo $ASCEND_HOME_PATH
/usr/local/Ascend/cann-8.5.0

cd /usr/local/Ascend/cann-8.5.0

# 可以看到 set_enc.sh
ls
aarch64-linux  cann_uninstall.sh  compiler  fwkacllib  mindstudio-toolkit  pkg_inc  set_env.sh  toolkit
arm64-linux    combo_script       conf      include    opp                 python   share       tools
bin            compat             devlib    lib64      ops_uninstall.sh    runtime  test-ops    var

# 在当前终端会话中  激活环境变量
# 每次新开终端都要 source 一次。建议把 source 命令加到 ~/.bashrc 里。
source /usr/local/Ascend/cann-8.5.0/set_env.sh

# 确认msprof安装成功
ls $ASCEND_HOME_PATH/tools/profiler/bin/msprof
/usr/local/Ascend/cann-8.5.0/tools/profiler/bin/msprof
```

查看设备状态

```bash
# 查看NPU设备状态
npu-smi info
# 可以看到设备名为 910B4 
+------------------------------------------------------------------------------------------------+
| npu-smi 25.5.1                   Version: 25.5.1                                               |
+---------------------------+---------------+----------------------------------------------------+
| NPU   Name                | Health        | Power(W)    Temp(C)           Hugepages-Usage(page)|
| Chip                      | Bus-Id        | AICore(%)   Memory-Usage(MB)  HBM-Usage(MB)        |
+===========================+===============+====================================================+
| 6     910B4               | OK            | 88.4        42                0    / 0             |
| 0                         | 0000:82:00.0  | 0           0    / 0          2875 / 32768         |
+===========================+===============+====================================================+
+---------------------------+---------------+----------------------------------------------------+
| NPU     Chip              | Process id    | Process name             | Process memory(MB)      |
+===========================+===============+====================================================+
| No running processes found in NPU 6                                                            |
+===========================+===============+====================================================+
```

验证python环境

```bash
#一行验证：能 import acl 并初始化即 OK
python3 -c "import acl;acl.init();acl.rt.set_device(0);print('runtime OK')"
runtime OK

# 如有异常，安装CANN 运行时依赖的 Python 包（缺一不可，否则跑不起来）
pip3install attrs cython numpy decorator sympy cffi pyyaml pathlib2 psutilprotobuf==3.20.0 scipy requests absl-py --user
```

**环境验证清单（确认2.1.2-2.1.4）**

进入下一步前，确认完成以下验证：

☐ echo $ASCEND_HOME_PATH 输出非空

☐ npu-smi info 至少显示 1 个 NPU，Health = OK

☐ ls $ASCEND_HOME_PATH/include/acl/acl.h 存在

☐ python3 -c "importacl;acl.init();acl.rt.set_device(0)" 不报错

☐ ls $ASCEND_HOME_PATH/tools/profiler/bin/msprof存在

---

## 代码下载

注意notebook创建文件夹有权限，自己摸索下

```bash
# wget 下载示例代码
wget https://ascend-lab.obs.cn-north-4.myhuaweicloud.com/AscendC-Labs/add_demo.zip

# 解压文件
unzip add_demo.zip
#
cd add_demo/ && ls
CMakeLists.txt  add.asc  build_and_run.sh  parse_msprof.py  run_with_msprof.sh  test_add_runner.sh  tools

add_demo/
├──add.asc              # Device kernel +Host
├──CMakeLists.txt       # cmake文件
├──build_and_run.sh     # 执行add|sub 的脚本文件，会生成 CPUFP64 Add golden
├──run_with_msprof.sh   # msprof 脚本文件 启动msprof 并执行profiling采集
└──parse_msprof.py      # 解析 add_customtask_time/op_statistic
```

源码导览

https://www.hiascend.com/edu/experiment/detail/1d0b0b790fb24947977d6d954112c016?tab=4

## 运行 Add Demo

```bash
cd add_demo
bash build_and_run.sh add
# 运行结果
--- Precision (NPU vs PyTorch CPU FP64 golden) ---
[Precision] MERE = 2.31711e-08  (FP32 pass if < 2^-13 = 0.00012207)
[Precision] MARE = 5.96044e-08  (FP32 pass if < 10*2^-13 = 0.0012207)
[Precision] PASS ✓
REFERENCE_VALUE=2.09999996
ACTUAL_VALUE=2.0999999
ABS_ERROR=5.96046448e-08
REL_ERROR=2.83831633e-08

--- Performance (kernel only, 不含 host↔device 拷贝) ---
[CPU] add_cpu average time:    3.151 ms
[NPU] kernel_add_npu average time (host wall): 0.047 ms
>>> NPU vs CPU speedup (host wall): 67.70 x
  （NPU 的纯硬件耗时可用 msprof 采集，更精确：见 run_with_msprof.sh）
============================================================
✓ 运行结束（更精确的 NPU 耗时可用 run_with_msprof.sh）
```

```bash
bash build_and_run.sh sub
# 运行结果
--- Precision (NPU vs PyTorch CPU FP64 golden) ---
[Precision] MERE = 1.33333  (FP32 pass if < 2^-13 = 0.00012207)
[Precision] MARE = 1.33333  (FP32 pass if < 10*2^-13 = 0.0012207)
[Precision] FAIL ✗
REFERENCE_VALUE=2.09999996
ACTUAL_VALUE=-0.699999988
ABS_ERROR=2.79999995
REL_ERROR=1.33333327
[Precision] sub 模式使用 Add golden，预期精度失败。

--- Performance (kernel only, 不含 host↔device 拷贝) ---
[CPU] add_cpu average time:    3.143 ms
[NPU] kernel_add_npu average time (host wall): 0.044 ms
>>> NPU vs CPU speedup (host wall): 71.36 x
  （NPU 的纯硬件耗时可用 msprof 采集，更精确：见 run_with_msprof.sh）
```

## 运行msprof 采集

```bash
# 在add_demo 目录下进行profiling数据采集，--elements N表示会采集1M（1048576）个float的add算子耗时
bash run_with_msprof.sh --elements 1048576
# 问题：输出这一行就没了
[INFO] 检测到 昇腾 A2 系列产品
```

**解决办法**

将脚本中

```sh
MSPROF_BIN=$(find "${ASCEND_HOME_PATH:-/usr/local/Ascend}" -name "msprof" -type f 2>/dev/null | head -1)
```

替换为

```sh
# 优先直接使用 PATH 里的 msprof，找不到再用安全规避 SIGPIPE 的 find 命令
if command -v msprof >/dev/null 2>&1; then
    MSPROF_BIN=$(command -v msprof)
else
    # 末尾加上 || true 吸收 find 遭遇 SIGPIPE 时的 141 错误码，防止 pipefail 杀掉脚本
    MSPROF_BIN=$(find "${ASCEND_HOME_PATH:-/usr/local/Ascend}" -maxdepth 6 -name "msprof" -type f 2>/dev/null | head -1 || true)
fi

if [ -z "${MSPROF_BIN}" ]; then
    echo "[ERROR] 找不到 msprof，请安装 CANN toolkit 后重试" >&2
    exit 1
fi
```

```sh
"${MSPROF_BIN}" \
    --output="${OUTPUT_DIR}" \
    --task-time=l1 \								# cann-8.5.0  环境下要使用 l1，源代码使用 l2
    --application="${SCRIPT_DIR}/build/demo add --golden ${REFERENCE_FILE} --elements ${ELEMENTS}" \
    2>&1 | tee "${OUTPUT_DIR}/msprof_collect.log"
```

msprof 结果

```bash
--- Performance (kernel only, 不含 host↔device 拷贝) ---
[CPU] add_cpu average time:    3.228 ms
[NPU] kernel_add_npu average time (host wall): 0.050 ms
>>> NPU vs CPU speedup (host wall): 64.37 x

[INFO] msprof 采集完成，开始解析 add_custom 耗时 ...

=== msprof task_time 采集到的 add_custom 耗时 ===
  样本数: 103
  平均:   30.50 us = 0.0305 ms
  最小:   27.66 us
  最大:   44.04 us
  累计:   3141.66 us = 3.14 ms
```

## 扩展实验

**A 修改参数大小**

修改 `bash run_with_msprof.sh --elements 1048576` 中 elements 参数大小

```bash
bash run_with_msprof-Copy1.sh --elements 16777216 
#
-- Performance (kernel only, 不含 host↔device 拷贝) ---
[CPU] add_cpu average time:    89.897 ms
[NPU] kernel_add_npu average time (host wall): 0.683 ms
>>> NPU vs CPU speedup (host wall): 131.71 x

[INFO] msprof 采集完成，开始解析 add_custom 耗时 ...

=== msprof task_time 采集到的 add_custom 耗时 ===
  样本数: 103
  平均:   664.62 us = 0.6646 ms
  最小:   655.97 us
  最大:   673.63 us
  累计:   68455.90 us = 68.46 ms
```

加速比更大了

**B 改 tileLength**

```c++
// 全局 kernel 配置常量：Host 与 Device 共享      .asc 文件
constexpruint32_t tileLength = 1024;
```

```bash
# 在add_demo 目录下，删除缓存编译文件
rm build/demo

# 在add_demo 目录下进行profiling数据采集（包含重新编译）
bash run_with_msprof.sh --elements 1048576
```

结果

```txt
--- Precision (NPU vs PyTorch CPU FP64 golden) ---
[Precision] MERE = 2.31711e-08  (FP32 pass if < 2^-13 = 0.00012207)
[Precision] MARE = 5.96044e-08  (FP32 pass if < 10*2^-13 = 0.0012207)
[Precision] PASS ✓
REFERENCE_VALUE=2.09999996
ACTUAL_VALUE=2.0999999
ABS_ERROR=5.96046448e-08
REL_ERROR=2.83831633e-08

--- Performance (kernel only, 不含 host↔device 拷贝) ---
[CPU] add_cpu average time:    3.146 ms
[NPU] kernel_add_npu average time (host wall): 0.063 ms
>>> NPU vs CPU speedup (host wall): 50.05 x

=== msprof task_time 采集到的 add_custom 耗时 ===
  样本数: 103
  平均:   47.69 us = 0.0477 ms
  最小:   45.50 us
  最大:   71.58 us
  累计:   4912.09 us = 4.91 ms
```

**C：改 numBlocks**

注释：tileLength 改回了 2048

```c++
// 用于计算的 block 数量，从8修改为4
constexpruint32_t numBlocks  = 4;
```

```bash
rm build/demo
bash run_with_msprof.sh --elements 1048576
```

实验结果

```bash
--- Precision (NPU vs PyTorch CPU FP64 golden) ---
[Precision] MERE = 2.31711e-08  (FP32 pass if < 2^-13 = 0.00012207)
[Precision] MARE = 5.96044e-08  (FP32 pass if < 10*2^-13 = 0.0012207)
[Precision] PASS ✓
REFERENCE_VALUE=2.09999996
ACTUAL_VALUE=2.0999999
ABS_ERROR=5.96046448e-08
REL_ERROR=2.83831633e-08

--- Performance (kernel only, 不含 host↔device 拷贝) ---
[CPU] add_cpu average time:    3.435 ms
[NPU] kernel_add_npu average time (host wall): 0.075 ms
>>> NPU vs CPU speedup (host wall): 46.09 x

=== msprof task_time 采集到的 add_custom 耗时 ===
  样本数: 103
  平均:   57.51 us = 0.0575 ms
  最小:   53.56 us
  最大:   82.66 us
  累计:   5923.02 us = 5.92 ms
```

性能下降了（用时接近两倍）

# 附录

修改后的run_msprof.sh 文件

```sh
#!/bin/bash
# ----------------------------------------------------------------------------
# Lab 2 —— 用 msprof 采集 NPU 算子真实耗时
#
# 用法：bash run_with_msprof.sh [--elements N]（自动识别产品）
# 输出：prof_output/ 目录下有 msprof 采集的 csv / json
# ----------------------------------------------------------------------------
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/tools/ascend_product.sh"
OUTPUT_DIR="${SCRIPT_DIR}/prof_output"
mkdir -p "${OUTPUT_DIR}"

ELEMENTS=1048576
while [[ $# -gt 0 ]]; do
    case "$1" in
        --elements)
            [[ $# -ge 2 && "$2" =~ ^[1-9][0-9]*$ ]] || { echo "[ERROR] --elements requires a positive integer" >&2; exit 2; }
            ELEMENTS="$2"
            shift 2 ;;
        -h|--help)
            echo "用法: $0 [--elements N]"
            exit 0 ;;
        *)
            echo "[ERROR] 用法: $0 [--elements N]" >&2
            exit 2 ;;
    esac
done
DEVICE_ID=${ASCEND_RT_VISIBLE_DEVICES:-}
DEVICE_ID=${DEVICE_ID%%,*}
DEVICE_ID=${DEVICE_ID:-0}
detect_ascend_product "$DEVICE_ID" || { echo "[ERROR] 无法识别当前 NPU 产品，请检查 npu-smi、驱动和设备状态" >&2; exit 1; }
echo "[INFO] 检测到 ${ASCEND_PRODUCT_SERIES}"

# 1. 加载环境
if [ -z "$ASCEND_HOME_PATH" ]; then
    if [ -f "/usr/local/Ascend/ascend-toolkit/set_env.sh" ]; then
        source /usr/local/Ascend/ascend-toolkit/set_env.sh
    elif [ -f "/usr/local/Ascend/cann/set_env.sh" ]; then
        source /usr/local/Ascend/cann/set_env.sh
    fi
fi

# 优先直接使用 PATH 里的 msprof，找不到再用安全规避 SIGPIPE 的 find 命令
if command -v msprof >/dev/null 2>&1; then
    MSPROF_BIN=$(command -v msprof)
else
    # 末尾加上 || true 吸收 find 遭遇 SIGPIPE 时的 141 错误码，防止 pipefail 杀掉脚本
    MSPROF_BIN=$(find "${ASCEND_HOME_PATH:-/usr/local/Ascend}" -maxdepth 6 -name "msprof" -type f 2>/dev/null | head -1 || true)
fi

if [ -z "${MSPROF_BIN}" ]; then
    echo "[ERROR] 找不到 msprof，请安装 CANN toolkit 后重试" >&2
    exit 1
fi

echo "[INFO] msprof: ${MSPROF_BIN}"

# 2. 先确保 demo 已编译
if [ ! -f "${SCRIPT_DIR}/build/demo" ]; then
    echo "[INFO] 还没编译 demo，先编译 ..."
    bash "${SCRIPT_DIR}/build_and_run.sh" add >/dev/null
fi
REFERENCE_FILE=${ADD_GOLDEN_FILE:-"${SCRIPT_DIR}/build/add_golden_fp64.bin"}
echo "[INFO] 生成 PyTorch CPU FP64 Add golden: ${REFERENCE_FILE}"
python3 "$SCRIPT_DIR/tools/add_reference.py" --elements "$ELEMENTS" --output "$REFERENCE_FILE"

# 3. 用 msprof 包住 demo
echo "[INFO] 开始用 msprof 采集 ..."
BEFORE_PROF_LIST=$(mktemp)
trap 'rm -f "$BEFORE_PROF_LIST"' EXIT
find "${OUTPUT_DIR}" -mindepth 1 -maxdepth 1 -type d -name 'PROF_*' -print | sort > "$BEFORE_PROF_LIST"
"${MSPROF_BIN}" \
    --output="${OUTPUT_DIR}" \
    --task-time=l1 \
    --application="${SCRIPT_DIR}/build/demo add --golden ${REFERENCE_FILE} --elements ${ELEMENTS}" \
    2>&1 | tee "${OUTPUT_DIR}/msprof_collect.log"

LATEST_PROF=$(comm -13 "$BEFORE_PROF_LIST" <(find "${OUTPUT_DIR}" -mindepth 1 -maxdepth 1 -type d -name 'PROF_*' -print | sort) | tail -1)
if [ -z "${LATEST_PROF}" ]; then
    echo "[ERROR] 本次 msprof 未生成新的 PROF_* 目录，拒绝复用历史采集结果" >&2
    exit 1
fi
if [ ! -d "${LATEST_PROF}/mindstudio_profiler_output" ]; then
    echo "[ERROR] 本次 msprof 目录缺少 mindstudio_profiler_output: ${LATEST_PROF}" >&2
    exit 1
fi

# 4. 自动解析 add_custom 的耗时
echo ""
echo "[INFO] msprof 采集完成，开始解析 add_custom 耗时 ..."
python3 "${SCRIPT_DIR}/parse_msprof.py" "${LATEST_PROF}"

echo "[INFO] 结果目录: ${LATEST_PROF}"

```

