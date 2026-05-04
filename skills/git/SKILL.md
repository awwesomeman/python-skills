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
| 建立 / 撰寫 Issue（標題、內文、DoD） | [git-workflow/SKILL.md](./git-workflow/SKILL.md) |
| 拆分大型 Issue / sub-issue / task list | [git-workflow/SKILL.md](./git-workflow/SKILL.md) |
| 建立分支 / 分支命名 | [git-workflow/SKILL.md](./git-workflow/SKILL.md) |
| 建立 PR / 撰寫 PR 描述 / `Closes #N` | [git-workflow/SKILL.md](./git-workflow/SKILL.md) |
| 決定 merge 策略（squash / merge / rebase）/ 撰寫 squash 訊息 | [git-workflow/SKILL.md](./git-workflow/SKILL.md) |
| 建立 git commit 訊息 | [conventional-commits/SKILL.md](./conventional-commits/SKILL.md) |
| 版本發布 / `cz bump` / CHANGELOG / tag / GitHub Release | [release-management/SKILL.md](./release-management/SKILL.md) |
| 規劃完整開發流程 | [git-workflow/SKILL.md §0](./git-workflow/SKILL.md) 為總圖，再依階段路由到對應 skill |
| 完整 release 流程（issue → branch → commit → PR → merge → 累積 → main 上 bump → tag → push --follow-tags → GitHub Release） | 三個 skill 全部載入 |

## Skill 簡表

| Skill | 定位 |
|-------|------|
| **conventional-commits** | Commit 訊息格式：type/scope/description、atomic commit、Issue Number、Signed-off-by、breaking change 標記 |
| **git-workflow** | 工作流規範：完整流程圖、Issue / sub-issue / PR / merge 規範、分支命名、tense-neutral 紀律、squash 訊息、禁止操作 |
| **release-management** | 版本發布：release-train 節奏、bump-on-main 紀律、hybrid CHANGELOG 工作流、cz bump、GitHub Release |
