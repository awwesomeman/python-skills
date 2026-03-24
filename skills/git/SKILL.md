---
name: jason-git-skills
description: Git 相關技能入口。當執行 git commit、建立分支、提交 PR、或需要遵循 commit 規範時使用。根據任務路由到對應的子 skill。
---

# Git 技能索引 (Git Skills Overview)

> 本 skill 是 Git 相關操作的入口。根據當前任務判斷應啟用哪個子 skill。

---

## 任務路由

| 任務 | 載入的 Skill |
|------|-------------|
| 建立 git commit | conventional-commits |
| 分支管理 / PR 流程 | git-workflow |
| 完整 git 操作流程 | conventional-commits + git-workflow |

## Skill 簡表

| Skill | 定位 |
|-------|------|
| **conventional-commits** | 遵循 Conventional Commits 規範建立標準化 commit message，含 type/scope/description 格式、Issue Number、Signed-off-by |
| **git-workflow** | Git 工作流規範：分支命名、commit 策略、PR 建立與合併流程 |
