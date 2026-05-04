---
name: git-workflow
description: Git 工作流規範。當建立 Issue、分支、PR、執行 merge 或規劃整體開發流程時使用。
---

# Git 工作流規範

## 何時使用此 Skill

當你需要：建立 Issue / 分支 / PR、決定 merge 策略、或規劃從 issue 到 release 的完整流程時。

## 0. 完整開發流程

```
Issue (#N) ──► branch <type>/<short-desc> ──► commits ──► PR ──► squash-merge to main ──┐
                                                                                         │
                                          ┌──────────────────────────────────────────────┘
                                          ▼
                  累積變更（on main）──► version bump ──► tag vX.Y.Z ──► push --follow-tags ──► GitHub Release
```

階段對應規範：Issue / branch / PR / merge → 本 skill；commit 訊息 → [`../conventional-commits/SKILL.md`](../conventional-commits/SKILL.md)；版本 bump / tag / CHANGELOG / GitHub Release → [`../release-management/SKILL.md`](../release-management/SKILL.md)（含 bump-on-main 紀律與 release-train 節奏）。

## 1. 分支命名規範

格式：`<type>/<short-description>`，可選帶 issue：`<type>/<issue>-<short-description>`

| 類型 | 範例 |
|------|------|
| `feat/` | `feat/user-auth`、`feat/123-user-auth` |
| `fix/` | `fix/login-timeout` |
| `docs/` | `docs/api-guide` |
| `refactor/` | `refactor/db-layer` |
| `hotfix/` | `hotfix/security-patch` |

> 本工作流採 trunk-based + squash merge，**不使用 `release/` 分支**：版本 bump 與 tag 一律在 `main` 上完成（見 [`../release-management/SKILL.md`](../release-management/SKILL.md) §2）。`hotfix/` 為 main 上緊急修補用，merge 後同樣在 main bump。

| 規則 | Why |
|------|-----|
| 全部小寫、`-` 分隔 | Windows/macOS 大小寫敏感性不一致；底線在終端機選取時容易誤判 |
| 簡潔 (2-4 字) | 終端機列表截斷時仍可辨識 |
| 不用個人名 (`feat/jason-fix`) | 分支應描述「做什麼」非「誰做」；個人名讓非當事人難以接手、PR 移交時也需改名 |

> 分支前綴採用與 commit `type` 對齊（`feat/`、`fix/`、`docs/`、`refactor/`），讓 issue / branch / commit / PR 整條動線視覺一致。

## 2. Issue 撰寫規範

### 標題

祈使句、描述性、< 70 字元。範例：`Login times out under high latency`、`Support OAuth login`。

可選：用 commit type 前綴（`feat: ...`、`fix: ...`）讓 issue / branch / commit / PR 視覺對齊；本專案採此風格時，整條動線一致即可，不採用時靠 label / milestone 分類也是主流做法。

### 內文模板（建議）

```markdown
## Problem
<為什麼這是個問題；現狀帶來什麼影響>

## Expected
<期望達成的結果；對外契約>

## Definition of Done
- [ ] <可驗證的完工條件 1>
- [ ] <可驗證的完工條件 2>
```

> 內文須遵循 §4 tense-neutral 紀律：**只寫永遠為真的事實**，不嵌入分支名 / SHA / 「awaiting PR」「[WIP]」等 status 字句。

### Sub-issue：當 issue 太大需要拆分

當 issue 範圍過大（無法一個 PR 完成、或需多人並行），拆成**父 + 子 issue**，每個子 issue 對應獨立可 merge 的 PR。

**機制**：用 GitHub 原生 Sub-issues（2024-10+），或在父 body 列 `- [ ] #<sub-id>` task list；兩者都會在 UI 同步顯示子 issue 的開/關**狀態**與進度，但**不會**自動關閉父 issue（避免提前丟失整體驗收節點）。父 body 在標準模板下方加一段：

```markdown
## Sub-issues
- [ ] #<id> <子任務 A>
- [ ] #<id> <子任務 B>
```

| 規則 | Why |
|------|-----|
| 子 issue 必須**獨立可 merge** | 假拆分讓子 PR 互相依賴，無法平行推進，失去拆分意義 |
| 子 PR 用 `Closes #<sub-id>`，不關父 | 父應在「整體驗收完成」時人工關閉，提前自動關會丟追蹤點 |
| 父 body 不嵌入子 PR SHA / 分支名 | 違反 §4 tense-neutral；GitHub 已自動渲染 task list 連結 |
| 子 branch base 在 main，不 nest 在父 branch | Nested branch 會卡 merge 順序、conflict 倍增 |

## 3. PR 工作流

**建立前**：分支已同步最新 main（rebase 或 merge 視團隊政策）、測試通過、無 conflict、commit 歷史符合 atomic。

**標題**：遵循 Conventional Commits、< 70 字元，結尾可帶 `(#issue)`。範例：`feat(auth): support OAuth login (#42)`（GitHub squash 時會自動 append `(#PR-number)`，與 issue `#N` 並存無妨）

### 描述模板

```markdown
## Summary
- <1-3 bullet points 描述變更>

## Test plan
- [ ] <驗證項目>

Closes #<issue-number>
```

> **`Closes #N`** 必寫於描述末——merge 後 GitHub 自動關閉 issue，避免人工漏關。

## 4. Issue / PR Body 紀律：Tense-Neutral

> Body **只寫永遠為真的事實**（spec、適用矩陣、設計 rationale、DoD）。**不要**嵌入 commit SHA、分支名、或「awaiting PR」「shipped on X」等 status 字句。

**Why**：(1) GitHub 已用 `(#N)` 反向連結 + Linked PR sidebar 自動串連，body 再寫一次冗餘；(2) squash-merge 後 SHA 變、分支被刪，status 字句立刻 rot；(3) 製造維護債——要記得回來改否則語意不一致。

| 該寫（spec / 永久事實） | 不該寫（status / 短暫狀態） |
|-------------------------|------------------------------|
| 規格、契約、適用情境、設計理由 | 「目前進度到哪」「在哪個分支」 |
| DoD checkbox：`- [x] tests pass` | DoD 綁分支：`- [x] tests on feat/X branch` |
| 為什麼這個 change 重要 | commit SHA `be50883`、`awaiting PR to main` |

> Status 用 GitHub 內建機制追蹤（labels、Linked PR、`Closes #N` 自動關閉），不寫進 body。

## 5. Merge 策略

> **預設 squash merge**，少數例外才用 merge commit 或 rebase。

| 策略 | 何時使用 | Why |
|------|----------|-----|
| **Squash merge**（預設） | 一般 feature / fix PR | main 線性、每筆 merge = 一個可獨立 revert 的單元 |
| **Merge commit** | 長期 feature branch、需保留多人協作 commit 歷史 | 保留分支結構作為 review 紀錄 |
| **Rebase merge** | 單作者短分支、commit 已 atomic | 線性歷史 + 保留每個 commit；風險：rewrite SHA |

### Squash merge 訊息

GitHub 預設會把「PR 標題 + 全部 commit 訊息」灌進 squash message。**必須覆寫** body 為：

```
<type>(<scope>): <description> (#<issue-number>)

<簡述變更與 Why，1-3 行>

Closes #<issue-number>
```

| Don't | Why |
|-------|-----|
| 保留預設 commit 列表 dump | main log 變雜訊，看不出這次 PR 真正做了什麼 |
| Squash 訊息違反 Conventional Commits | 任何 changelog / SemVer 工具（commitizen、semantic-release 等）都需要正確 type 才能分類 |

## 6. 禁止事項與安全

未經使用者明確許可，**禁止**：

| 禁止 | Why |
|------|-----|
| Force push（任何情境，特別是 main） | 覆寫共享 / 他人歷史 |
| Amend 已推送的 commit | 改寫共享歷史 |
| `--no-verify` | 跳過 pre-commit hooks |
| `git reset --hard` / `clean -f` / `checkout .` / `restore .` | 丟失未提交或未追蹤的變更 |

安全：提交前確認無敏感資訊（`.env`、credentials、private keys）；用 `.gitignore` 排除敏感檔；大型二進位用 Git LFS；不提交 IDE 設定檔。

## 提交前檢查清單

- [ ] 分支名稱符合 `<type>/<description>`、全小寫、`-` 分隔、非個人名？
- [ ] Issue 標題祈使句、描述性、< 70 字元、無 status 字句？
- [ ] 大型 issue 已拆 sub-issues，且子 issue 各自獨立可 merge？
- [ ] Commit 訊息遵循 Conventional Commits（見對應 skill）？
- [ ] PR 標題 < 70 字元、遵循 Conventional Commits？
- [ ] PR 描述末有 `Closes #N`（子 issue 用子 id，不關父）？
- [ ] Issue / PR body 只寫永遠為真的事實，無 SHA / 分支名 / 進度字句？
- [ ] Squash merge 訊息已覆寫為 Conventional Commits 格式（不留預設 dump）？
- [ ] 未經許可未使用禁止操作（force push、`--no-verify`、`reset --hard` 等）？
- [ ] 沒有敏感資訊被提交？
