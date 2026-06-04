---
name: sync-before-dev
description: 开发前将 feature/jingwc rebase 到 develop 最新代码，自动检查工作区、拉取、变基、可选推送
---


# Git Rebase Sync — 开发前同步最新代码

每次开始开发前，执行此 skill 将 `feature/jingwc` 分支变基到 `develop` 最新代码。

## 固定参数

- **目标分支**：`develop`（集成分支，所有 feature 分支的基准）
- **工作分支**：`feature/jingwc`（你的开发分支）
- **远程仓库**：`origin`
- **推送行为**：询问用户是否需要推送到远程

## 执行步骤

按顺序执行以下每个步骤，全部完成后在最后给出清晰的结果摘要。

### Step 1 — 检查工作区状态

```bash
git status --short
```

- 如果有未提交的修改，**停下** → 提示用户先 `git stash` 或 commit，等用户处理后再继续
- 如果有未跟踪文件（`??`），可以忽略继续

### Step 2 — 确认当前分支

```bash
git branch --show-current
```

- 如果当前不在 `feature/jingwc`，先 `git checkout feature/jingwc`
- 如果有同名远程分支 `origin/feature/jingwc` 且存在远程更新，先 `git pull origin feature/jingwc` 拉取远程最新的自己的分支

### Step 3 — 拉取 develop 最新代码

```bash
git fetch origin develop
```

检查 fetch 是否成功。

### Step 4 — Rebase 到 develop

```bash
git rebase origin/develop
```

- 如果 rebase 成功 → 进入 Step 5
- 如果出现冲突（exit status != 0）：
  - 列出冲突文件：`git diff --name-only --diff-filter=U`
  - 告知用户冲突内容，**不要自动解决冲突**
  - 提示用户手动解决后执行 `git rebase --continue`，或执行 `git rebase --abort` 放弃

### Step 5 — 显示结果

```bash
git log --oneline -5
```

展示当前分支最新的 5 个提交，让用户确认变基成功。

### Step 6 — 是否推送

询问用户：`feature/jingwc 已更新到最新。是否需要 force push 到远程？`

- 用户选择是 → `git push --force-with-lease origin feature/jingwc`
- 用户选择否 → 跳过

## 结果摘要模板

完成时输出：

```
✅ feature/jingwc 已同步到 develop 最新代码

| 步骤 | 状态 |
|------|------|
| 工作区检查 | ✅ 干净 |
| 分支切换 | feature/jingwc |
| Fetch develop | ✅ 成功 |
| Rebase | ✅ 无冲突 |
| 当前 HEAD | <commit hash> |

💡 可以开始开发了！
```
