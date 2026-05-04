---
name: jpan-git
description: Git 相關技能入口。當執行 git commit、建立分支、提交 PR、撰寫 CHANGELOG、執行版本發布（release / bump / SemVer / tag / GitHub Release）、或需要遵循 commit 規範時使用。根據任務路由到對應的子 skill。
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

---

## 文件權責矩陣（誰該承載什麼資訊）

> 跨 skill 共用規則。撰寫 commit body / PR description / CHANGELOG / docstring 前，先確認資訊應該落在哪份文件——錯位會造成重複、過時、或在錯的地方被搜尋。

| 資訊類型 | 主要位置（permanent home） | 次要位置（可重疊） | 不該出現在 |
|---------|------------------------|-------------------|-----------|
| **What 變了**（一句話） | commit 標題 | PR 標題（Conventional Commits + `(#issue)`，squash 自動 append `(#PR)`） | — |
| **Why 變了**（motivation、取捨、副作用） | commit body | PR description `## Summary` 可精簡敘述（reviewer 視角） | 完整長段落不必在 PR description 複製貼上 |
| **怎麼 review**（測試步驟、screenshot、reviewer 該關注的點） | PR description `## Test plan` | — | commit body（reviewer-only 資訊不必進 git log） |
| **逐項變更清單**（新增的 field/function/test 名稱、檔案路徑、test 數量） | diff 自身（`git show`、PR Files tab） | — | commit body、CHANGELOG（diff 已呈現） |
| **User-facing 行為差異**（API 變動、回傳格式） | CHANGELOG entry | commit body 可簡述（特別是 `feat:` / `feat!:`） | 完整下游影響說明以 CHANGELOG 為單一資料源 |
| **Breaking change 標記** | commit body `BREAKING CHANGE:` footer（Conventional Commits spec，驅動 SemVer / changelog 工具） | — | — |
| **完整升級指引 / Migration note** | CHANGELOG `### Removed` / `### Changed` 條目本身（KaC 無 Migration section） | commit body 一行摘要可附於 `BREAKING CHANGE:` footer | 詳細多步驟升級不寫進 commit body（user 不讀 git log） |
| **概念說明 / 使用範例 / 參數語意** | docstring、README、ARCHITECTURE.md | — | commit body、CHANGELOG（不是教學文件） |
| **設計依據 / 數理推導 / pipeline 圖** | ARCHITECTURE.md、`docs/` | — | commit body、CHANGELOG |
| **Issue / PR 追蹤連結** | commit 標題 `(#issue)`、commit body `Refs #N`、CHANGELOG entry `(#PR)`、PR description `Closes #N` | — | commit body 不用 `Closes #N`（會提前觸發關閉） |

### 三個經驗法則

1. **「diff 看得到的不寫進 commit body」** — body 補充 diff 看不出來的 why
2. **「讀者不同，內容可重疊但不必複製貼上」** — 下游 user 讀 CHANGELOG（升級判斷），reviewer 讀 PR description（review），維護者讀 commit body（git blame 時的 why）。Why 在三處都可以出現，但深度與視角不同：commit body 是永久詳述、PR description 是 reviewer 視角的精簡版、CHANGELOG 是 user 視角的影響面
3. **「主要位置才是單一資料源」** — 同一資訊出現在多處時，以「主要位置」為準；其他地方的副本若過時不更新也無妨
