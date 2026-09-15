---
title: "Python调试技巧"
date: 2026-09-15T14:51:51+08:00
draft: false
slug: "Python调试技巧"
categories: []
---

# Python 调试技巧

# 1.变量信息

```
x = 10
print(f"{x=}")		# x
```

---

# 2.打印方法名

```PYTHON
import inspect

# 获取方法名
def get_func_name():
    return inspect.currentframe().f_back.f_code.co_name

def function_name()
    # 使用
    print(f"{get_func_name()} 测试完成✅")
```

```
function_name 测试完成✅
```

---

# 3.快速定位

# 定义位置

IDE 编辑器内 `Ctrl` + `左键` 定位到变量或方法的定义位置

# 打印的位置

在IDE终端中快速跳转 定位函数位置 

## **自定义**

```python
import inspect

def dbg(*vars):
    # 获取调用dbg这一行的代码位置
    caller = inspect.getframeinfo(inspect.currentframe().f_back)
    # 【关键格式】IDE识别：路径:行号
    loc = f"{caller.filename}:{caller.lineno}"
    # 拼接变量打印（同时保留 {var=} 风格）
    parts = []
    for v in vars:
        parts.append(f"{v=}")
    msg = ", ".join(parts)
    print(f"[{loc}] {caller.function} | {msg}")

def test():
	x = 10
	dbg(x)
	x = [i for i in range(10)]
	dbg(x)
```

## logging（更规范，支持点击跳转）

logging 原生自带`pathname`、`lineno`：

```python
import logging

logging.basicConfig(
    format="%(pathname)s:%(lineno)d | %(funcName)s | %(message)s"
)
log = logging.getLogger(__name__)
# 使用
x = 10
log.debug(f"{x=}")
x = [i for i in range(10)]
log.debug(f"{x=}")
```

运行无输出，`logging` 默认**只输出 WARNING 及以上级别**，`debug` 级别默认被过滤，所以你直接运行看不到任何打印。 有两种解决方式：

## 方案 1：设置日志级别（推荐）

```
logging.basicConfig(
    level=logging.DEBUG,  			# 加上这一行，开启debug输出,意思是对 debug 以及以上级别生效
    format="%(pathname)s:%(lineno)d | %(funcName)s | %(message)s"
)
```

## 方案 2：改用 log.info()

info 默认是打开的，但是语义上 info 不是调试信息：

```
x = 10
log.info(f"{x=}")
x = [i for i in range(10)]
log.info(f"{x=}")
```

## 结果

运行输出示例（**VSCode 内置终端里，路径：行号 可以 Ctrl + 左键跳转**）：

```
F:\PythonTemp\onlyone.py:10 | <module> | x=10
F:\PythonTemp\onlyone.py:12 | <module> | x=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
```

# 4.python 多行执行

**目的：**直接将一段程序复制到 Terminal 运行，避免创建文件，python 命令执行文件，删除文件

## **python 交互式 REPL 粘贴模式**

> 1.敲 `python` 进入 `>>>`
>
> 2.Python3.10+：**F3** 开启 paste 模式
>
> 3.粘贴整块代码，按回车运行

## **powershell**

> 格式
>
> ```powershell
> # python -c @"多行代码"
> ```
>
> 例子
>
> ```powershell
> python -c @"
> import logging
> logging.basicConfig(
>     level=logging.DEBUG,
>     format="%(pathname)s:%(lineno)d | %(funcName)s | %(message)s"
> )
> log = logging.getLogger(__name__)
> x = 10
> log.debug(f"{x=}")
> x = [i for i in range(10)]
> log.debug(f"{x=}")
> "@
> ```
