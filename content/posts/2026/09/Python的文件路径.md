---
title: "Python的文件路径"
date: 2026-09-15T14:51:38+08:00
draft: false
slug: ""
categories: []
---

# Python 的路径

# A.路径

对比 `os.path` 和 `Path` 对文件路径的操作

```python
import os

from pathlib import Path
```

---

# 1.创建

```Python
# 字符串格式
filepath = "/home/user/data/signal_001.h5"

# Path格式
p = Path("/home/user/data/signal_001.h5")
# 全路径名：/home/user/data/signal_001.h5
print(p)  									
```

# 2.获取文件名

## 有后缀name

```Python
filename = os.path.basename(filepath)

filename = p.name 
```

## 无后缀stem

```Python
# 方法 A: os.path
base_name = os.path.splitext(os.path.basename(filepath))[0]

# 方法 B: 纯字符串切片
filename = os.path.basename(filepath)
base_name = filename[:filename.rindex('.')]

# Path
base_name = p.stem  # stem 意为"词干/主干"
```

# 3. 获取文件后缀名 (`.h5`)

- **字符串**:

  ```
  ext = os.path.splitext(filepath)[1]
  ```

- **Path **:

  ```
  ext = p.suffix
  ```

# 4. 修改后缀名

- **字符串**:

  ```Python
  new_filepath = os.path.splitext(filepath)[0] + ".csv"
  ```

- **Path**:

  ```Python
  new_filepath = p.with_suffix(".csv") 
  ```

# 5. 拼接路径

- **字符串**:

  ```Python
  savedir = "/home/user/output"
  # os.path.join 会自动处理系统的斜杠方向
  new_filepath = os.path.join(savedir, os.path.basename(filepath)) 
  ```

- **Path**

  ```Python
  savedir = Path("/home/user/output")
  # Path 对象重载了 "/" 运算符，拼接极其自然
  new_filepath = savedir / p.name 
  ```

# 6. 在原文件名后追加字符 (例如保存为 `xxx_norm.h5`)

- **字符串**:

  ```Python
  base = os.path.splitext(os.path.basename(filepath))[0]
  ext = os.path.splitext(filepath)[1]
  new_filename = f"{base}_norm{ext}"
  new_filepath = os.path.join(savedir, new_filename)
  ```

- **Path**:

  ```Python
  # 结合 stem 和 suffix，配合 f-string 非常干净
  new_filename = f"{p.stem}_norm{p.suffix}"
  new_filepath = savedir / new_filename
  ```

