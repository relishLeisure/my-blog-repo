---
title: "Hugo Operation Memo"
date: 2026-08-24T14:50:02+08:00
draft: true
slug: 
categories: [笔记]
---



## 新建模板文件

```cmd
# 命令
hugo new --kind <template-name> path/<filename>

hugo new --kind default posts/2026/08/CUDA复习.md

# 示例
E:\github_pages\my-blog-repo>hugo new --kind default posts/2026/thoughts/2608随便写.md
# 结果
WARN  deprecated: project config key languageCode was deprecated in Hugo v0.158.0 and will be removed in a future release. Use locale instead.
Content "E:\\github_pages\\my-blog-repo\\content\\posts\\2026\\thoughts\\2608随便写.md" created
```

模板位置：/archetypes/default.md

```markdown
---
title: "{{ replace .File.ContentBaseName "-" " " | title }}"
date: {{ .Date }}
draft: true
slug: "{{ .File.ContentBaseName }}"
categories: []
---
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

下载下来需要安装

```cmd

```

