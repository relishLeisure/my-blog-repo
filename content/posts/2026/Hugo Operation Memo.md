---
title: "Hugo Operation Memo"
date: 2026-08-24T14:50:02+08:00
draft: true
slug: 
categories: [笔记]
---



## 新建模板文件

```cmd
hugo new quickstart <template-name>
```

文件内容

```markdown
```

## 编译

```cmd
# 编译指的是把markdown等文件，编译成静态页面
hugo server --gc -D				# server 表示在本地启动服务，gc 表示清理缓存，-D 表示草稿也进行编译
```

# 其他文件

## Jupyter Notebook

### 1 转成markdown之后使用hugo

将 `.ipynb` 转换为 `.md`

```cmd
jupyter nbconvert --to markdown your_notebook.ipynb
```

### 2 Quarto

```cmd
jupyter nbconvert --to markdown your_notebook.ipynb
```

