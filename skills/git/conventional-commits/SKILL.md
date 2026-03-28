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

## 重要規則

| 規則 | 原因 |
|------|------|
| **禁止加入任何 emoji** | 破壞自動化解析（changelog 生成、SemVer bump） |
| **禁止 AI 簽名檔**（如 Co-Authored-By: Claude） | 污染 git log，非人類貢獻不應記入 |
| **禁止手動撰寫用戶 name/email** | git 會從 config 讀取，手動寫容易出錯且不一致 |
| description 小寫開頭、不加句號 | Conventional Commits 規範要求 |
| description < 50 字元 | 超過會在 git log --oneline 中被截斷 |
| body 說明「為什麼」而非「做了什麼」 | 標題已描述 what，body 提供 why 才有額外價值 |

## 支援的 Type 類型

| Type | 說明 |
|------|------|
| `feat` | 新增功能 (SemVer MINOR) |
| `fix` | 修復 bug (SemVer PATCH) |
| `docs` | 文件變更 |
| `style` | 程式碼格式調整 (不影響邏輯) |
| `refactor` | 重構 (不新增功能或修復 bug) |
| `perf` | 效能優化 |
| `test` | 新增或修改測試 |
| `build` | 建置系統或外部依賴變更 |
| `ci` | CI 設定變更 |
| `chore` | 其他維護性變更 |
| `revert` | 還原先前的 commit |

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

### 3. 詢問 Issue Number

使用 AskUserQuestion 詢問：「請問這個 commit 關聯的 Issue Number 是什麼？（如無則可留空）」

- 有 Issue → `<type>(<scope>): <description> (#<issue-number>)`
- 無 Issue → `<type>(<scope>): <description>`

### 4. 執行 Commit

使用 `-s` 參數自動附上 Signed-off-by（git 從 config 讀取 user.name/email，不要手動撰寫）。

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

## 提交前檢查清單

> 在執行 `git commit` 前，逐項核對以下清單。未通過則不得執行 commit。

- [ ] type 選擇正確？（feat/fix/refactor 不要混用）
- [ ] description 使用祈使句、小寫開頭、< 50 字元？
- [ ] 有 body 時，說明的是「為什麼」而非「做了什麼」？
- [ ] 沒有 emoji、沒有 AI 簽名檔？
- [ ] 使用了 `-s` 參數？（前提：環境已設定 `git config user.name` 和 `user.email`，否則會報錯）
- [ ] 有關聯 Issue 時已附上 `(#number)`？
