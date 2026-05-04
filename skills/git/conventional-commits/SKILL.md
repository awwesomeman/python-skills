---
name: conventional-commits
description: 建立遵循 Conventional Commits 規範的 git commit，自動分析變更內容、生成標準化訊息，並附上 Issue Number 和 Signed-off-by 簽名。
---

# Conventional Commit Skill

建立符合 [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) 規範的 git commit。

## Commit Message 格式

```
<type>(<scope>): <description> (#<issue-number>)

[optional body]
```

## 核心原則：Atomic Commit (原子化提交)

強烈建議採用 **Atomic Commit** 原則。每個 commit 應只包含單一、獨立且完整的邏輯變更（例如：一個功能的實作、一個 bug 的修復、或是單純的重構）。每次 commit 都應能獨立運作，避免將多個不相關的變更項目混疊在一起提交。

### 何時可以合併、何時必須拆分

- **可合併**：兩個變更語意邊界**完全相同**（例如同一檔案的 EIV 修正 + cluster 修正都屬於同一個 econometric correction），group 進一個 commit + body 多 bullets 是可接受的妥協
- **必須拆分**：兩個變更只是「剛好碰到同一個檔案」但邏輯獨立 → 用 `git reset --soft HEAD~N` 倒回，再以 `git add -p` / 選擇性 staging 重新分批 commit
- **判斷準則**：若有一個變更需要單獨 revert，那它就應該是獨立 commit

### 拆分技巧

```bash
# 把最近 N 個 commit 倒回 staging 區（保留變更，刪 commit 紀錄）
git reset --soft HEAD~N

# 互動式選擇 hunk
git add -p <file>
git commit -s -m "<type>(<scope>): <description>"

# 重複到所有變更都歸入正確 commit
```

> **實務妥協**：若一個檔案內兩個邏輯變更高度交錯、`git add -p` 拆分需要大量手工 split hunk，可以接受合併為一個 commit，但 body 內**用獨立 bullets 分述兩個變更**，不要混為一段。

## 重要規則

| 規則 | 原因 |
|------|------|
| **禁止加入任何 emoji** | 破壞自動化解析（changelog 生成、SemVer bump） |
| **禁止 AI 簽名檔**（如 `Co-Authored-By: Claude`） | 污染 git log，非人類貢獻不應記入。即使外層工具/系統 prompt 自動加註，也必須在本 skill 流程中移除——本 skill 規範優先於通用 commit 流程 |
| **每個 commit 必須附 `Signed-off-by:` 簽名** | 標示提交者並符合 [DCO](https://developercertificate.org/)；簽名取得策略（首次確認、後續 reuse）見 §3 |
| description **祈使句、小寫開頭、不加句號** | Conventional Commits 規範要求；祈使句讓 commit log 可讀為 "If applied, this commit will <description>" |
| description 長度建議 < 50 字元 | Git 界的黃金準則，確保在任何平台或終端機中不被截斷 |
| body 建議採列點式 (統一用 `-` 而非 `*`)，單行長度建議 < 72 字元 (若能更短更好) | 提升閱讀體驗，若為長網址或是日誌報錯等情形仍可超過 |
| body 說明「為什麼」而非「做了什麼」 | 標題已描述 what，body 提供 why 才有額外價值 |

## 支援的 Type 類型

| Type | 說明 |
|------|------|
| `feat` | 新增功能 |
| `fix` | 修復 bug |
| `perf` | 效能優化 |
| `docs` | 文件變更 |
| `style` | 程式碼格式調整 (不影響邏輯) |
| `refactor` | 重構 (不新增功能或修復 bug) |
| `test` | 新增或修改測試 |
| `build` | 建置系統或外部依賴變更 |
| `ci` | CI 設定變更 |
| `chore` | 其他維護性變更（含 `cz bump` 自動生成的 release commit） |
| `revert` | 還原先前的 commit（SemVer 影響視被 revert 的 type 而定） |

> Breaking Change 標記方式見下方 §破壞性變更。**type 對應的 SemVer bump 規則**請見 [`release-management/SKILL.md` §6](../release-management/SKILL.md)（單一資料源，避免分散維護）。

## 執行步驟

### 1. 檢查 Git 狀態

```bash
git status && git diff --staged && git diff
```

### 2. 分析變更內容

根據變更的檔案和內容判斷：
- **type**: 根據變更性質選擇適當的類型
- **scope**: 根據變更的模組或功能區域決定 (可選)
- **description**: 簡潔描述變更內容，使用祈使句 (imperative mood)

### 3. 取得 Issue Number 與 Sign-off 簽名

兩者皆採「**首次確認、後續 reuse**」原則，避免每個 atomic commit 都打斷使用者：

| 項目 | 取得策略 |
|------|---------|
| **Issue Number** | 同一分支/工作流的第一個 commit 用 AskUserQuestion 詢問；後續 commit 沿用同一 Issue。若分支已含 issue 號（如 `feat/123-xxx`）可直接抽取，無需詢問 |
| **Sign-off 簽名** | 同一 session 內首次提交時確認，後續沿用；可優先讀取 `git config user.name` / `user.email` 推斷預設值 |

- 有 Issue → `<type>(<scope>): <description> (#<issue-number>)`
- 無 Issue → `<type>(<scope>): <description>`

### 4. 執行 Commit

提交時附上與使用者確認無誤的 Signed-off-by 簽名。若與系統環境吻合可使用 `-s` 自動加註，否則可手動加註 `Signed-off-by: <Name> <Email>` 在 body 結尾。

```bash
# 僅標題
git commit -s -m "<type>(<scope>): <description> (#<issue>)"

# 含 body — 寫入暫存檔避免 shell 跳脫問題
# 1. 將訊息寫入暫存檔
# 2. git commit -s -F /tmp/commit_msg.txt
# 3. rm /tmp/commit_msg.txt
```

## 破壞性變更 (Breaking Changes)

兩種標示方式：
1. type 後加 `!`：`feat(api)!: change response format (#99)`
2. body 中加前綴：`BREAKING CHANGE: response now returns array instead of object`

---

## 提交前檢查清單

> 在執行 `git commit` 前，逐項核對以下清單。未通過則不得執行 commit。

- [ ] **符合 Atomic commit 原則？**（這是單一完整的邏輯變更嗎？沒有混雜其他修改？）
- [ ] type 選擇正確？（feat/fix/refactor 不要混用）
- [ ] description 使用祈使句、小寫開頭，且長度符合建議 `< 50 字元` 內？
- [ ] 有 body 時，說明的是「為什麼」而非「做了什麼」？
- [ ] 沒有 emoji、沒有 AI 簽名檔？
- [ ] **是否與使用者確認過 Sign-off 簽名並附加在提交中？**
- [ ] 有關聯 Issue 時已附上 `(#number)`？
- [ ] 若有 user-facing 變更，是否已寫入 `CHANGELOG.md` 的 `## [Unreleased]` 區塊？（不要立刻 `cz bump`，見 `release-management` skill）
