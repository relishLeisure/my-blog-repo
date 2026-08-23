https://relishleisure.github.io/my-blog-repo/

# 使用说明



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
