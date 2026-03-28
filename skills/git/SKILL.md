---
name: jason-git-skills
description: Git 相關技能入口。當執行 git commit、建立分支、提交 PR、或需要遵循 commit 規範時使用。根據任務路由到對應的子 skill。
---

# Git 技能索引 (Git Skills Overview)

> 本 skill 是 Git 相關操作的入口。根據當前任務判斷應啟用哪個子 skill。

---

## 任務路由

判斷任務類型後，以**本檔案所在目錄**為基準，**直接讀取**對應子目錄的 SKILL.md 並依照規範執行，不需要詢問使用者確認。若父層與子層規則衝突，以子層為準。

| 任務 | 載入的 Skill（相對於本目錄） |
|------|------|
| 建立 git commit | [conventional-commits/SKILL.md](./conventional-commits/SKILL.md) |
| 分支管理 / PR 流程 | [git-workflow/SKILL.md](./git-workflow/SKILL.md) |
| 完整 git 操作流程 | [conventional-commits/SKILL.md](./conventional-commits/SKILL.md) + [git-workflow/SKILL.md](./git-workflow/SKILL.md) |

## Skill 簡表

| Skill | 定位 |
|-------|------|
| **conventional-commits** | 遵循 Conventional Commits 規範建立標準化 commit message，含 type/scope/description 格式、Issue Number、Signed-off-by |
| **git-workflow** | Git 工作流規範：分支命名、commit 策略、PR 建立與合併流程 |
