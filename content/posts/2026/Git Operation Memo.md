---
title: "Git Operation Memo"
date: 2026-08-24T14:50:02+08:00
draft: false
slug: 
categories: [Git]
---

> 分支相关操作？

```cmd
# 查看分支			-a 查看所有
git branch
git branch -a 	
 
# 切换分支
git checkout branch-name
git switch branch-name

# 分支改名
# 1. 修改当前分支名
git branch -m <new-branch-name>
# 2. 修改指定分支名
git branch -m <old-branch-name> <new-branch-name>
# 3. 如果旧分支已经推送到远程了，改名后需要把远程的旧分支删掉，再推送新分支：
git push origin --delete <old-branch-name>
git push origin -u <new-branch-name>

# 分支同步
# 1.当前分支从其他分支同步
git fetch origin
git merge origin/<branch-name>

# 2.当前分支推送到其他分支
# 第一次推送当前分支（建立远程关联）
git push -u origin <branch-name>
# 之后再次推送，直接输入：
git push
```

> 本地远程仓库不同步？

1. 本地同步远程



2. 本地推送到远程



3. 有差别需要修改