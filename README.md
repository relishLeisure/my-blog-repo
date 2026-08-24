# 我的个人博客

https://relishleisure.github.io/my-blog-repo/

# 使用说明

1.克隆repo

```cmd
mkdir -dir-name-
git clone https://github.com/relishLeisure/my-blog-repo.git
cd my-blog-repo

# 切换到archive分支
git checkout archive 
# (注: 如果你的 Git 版本较新，也可以使用 git switch archive)
```

2.项目结构

```cmd
my-blog-repo/
├── archetypes/			# 存放新建 Markdown 文章的 Front Matter 模板
├── content/			# 存放你的 Markdown 文章源文件
├── docs/				# hugo 编译后生成的静态网页文件，默认名为 public
├── layouts/
├── resources/
├── screenshots/
├── scripts/
├── static/				 # 存放静态资源（注：如 static/img）
└── themes/				 # 存放你下载的 Hugo 主题
├── migration.log
├── README.md
├── requirements.txt
└── hugo.toml     		 # 博客的全局配置文件
```

3.配置与使用

- content 文件夹中写markdown，图片文件路径放置在/img

- 配置hugo.toml

```toml
# 替换为你的 GitHub Pages 实际地址
# Hugo Configuration for ezyang's blog
baseURL = 'https://relishleisure.github.io/my-blog-repo/'
languageCode = 'cn-zh'
title = "Truman's blog"
theme = 'ashley'
publishDir = "docs"
```

- 生成静态文件

```cmd
# 建议先通过本地启动服务查看（-D 表示会编译草稿）
hugo server -D

# 生成静态文件
hugo 
```

- 上传到

```cmd
git add .
git commit -m "commit message"
git push
```

- github pages 略

# Q&A

> **我以后要自己创建年份文件夹和_index.md 吗？**
>
>
> • 分两种情况：
>
>   部署到 GitHub 时：不用。 CI 里保留的 "Generate year/month archives" 脚本会在构建时自动扫描 content/posts/ 下的年份目
>   录，自动生成 content/years/年份/_index.md，所以新年份上线 GitHub 是自动的。
>
>   本地预览（hugo server）时：只有"第一次出现的新年份"需要手动建一个文件。 例如以后写第一篇 2027 年的文章时，建 content/
>   years/2027/_index.md，内容就 5 行：
>
> ---
> ```markdown
>   ---
>   title: "2027"
>   layout: archive
>   ---
> ```
>
>
>   ---
>
>   - 已有年份（比如 2026）不用再动，加新文章到 content/posts/2026/ 即可，年份页会自动带上。
>   - 月份文件（2026/08/_index.md 这种）本地可建可不建，archives 页面没有链接月份页，只是 CI 会顺手生成。
>   - 如果哪天忘了建，本地点年份会 404，但 GitHub 上仍然正常（CI 会自动补）。
