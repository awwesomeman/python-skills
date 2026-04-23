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

## 重要規則

| 規則 | 原因 |
|------|------|
| **禁止加入任何 emoji** | 破壞自動化解析（changelog 生成、SemVer bump） |
| **禁止 AI 簽名檔**（如 Co-Authored-By: Claude） | 污染 git log，非人類貢獻不應記入 |
| **與使用者確認 Sign-off 簽名** | 每次提交前預設帶入使用者第一次提供的簽名檔（或系統 config）並要求確認 |
| description 小寫開頭、不加句號 | Conventional Commits 規範要求 |
| description 長度建議 < 50 字元 | 這是 Git 界的黃金準則，能確保在任何平台或終端機中不被截斷 |
| body 建議採列點式 (統一用 `-` 而非 `*`)，單行長度建議 < 72 字元 (若能更短更好) | 提升閱讀體驗，若為長網址或是日誌報錯等情形仍可超過 |
| body 說明「為什麼」而非「做了什麼」 | 標題已描述 what，body 提供 why 才有額外價值 |

## 支援的 Type 類型

| Type | 說明 | SemVer 影響 |
|------|------|-------------|
| `feat` | 新增功能 | **MINOR** bump |
| `fix` | 修復 bug | **PATCH** bump |
| `perf` | 效能優化 | **PATCH** bump |
| `docs` | 文件變更 | 不觸發 bump |
| `style` | 程式碼格式調整 (不影響邏輯) | 不觸發 bump |
| `refactor` | 重構 (不新增功能或修復 bug) | 不觸發 bump |
| `test` | 新增或修改測試 | 不觸發 bump |
| `build` | 建置系統或外部依賴變更 | 不觸發 bump |
| `ci` | CI 設定變更 | 不觸發 bump |
| `chore` | 其他維護性變更（含 `cz bump` 自動生成的 release commit） | 不觸發 bump |
| `revert` | 還原先前的 commit | 不觸發 bump |

> **Breaking Change → MAJOR bump**：在 type 後加 `!`，或在 body 中加 `BREAKING CHANGE:` 前綴。

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

### 3. 與使用者確認：Issue Number & Sign-off 簽名

使用 AskUserQuestion 詢問/確認以下資訊：
1. **Issue Number**：「請問這個 commit 關聯的 Issue Number 是什麼？（如無則可留空）」
2. **Sign-off 簽名**：「請確認本次提交的簽名（預設使用您第一次提供的簽名檔或 git config）」

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

## Commitizen 自動版本管理

> 建議使用 [commitizen](https://commitizen-tools.github.io/commitizen/) 進行語意化版本管理。請確保 `pyproject.toml` 已正確設定 `[tool.commitizen]`。

### cz commit — 互動式提交

```bash
cz commit   # 或縮寫 cz c
```

以互動問答引導填寫 type / scope / description / breaking change，確保格式符合規範。**建議在不確定格式時使用**，取代手動 `git commit -m`。

### cz bump — 自動版本 Bump

```bash
# 分析自上次 tag 以來的 commit → 決定版本 → 更新 pyproject.toml → 更新 CHANGELOG.md → 建立 commit + tag
cz bump

# 預覽，不實際執行
cz bump --dry-run

# 強制指定版本
cz bump --increment MAJOR   # 或 MINOR / PATCH
```

`cz bump` 執行後會自動生成一個版本 commit，格式為：

```
chore(release): vX.Y.Z
```

> 此 commit 由工具自動生成，**請勿手動修改或仿造**。

### SemVer Bump 觸發規則速查

| 條件 | 版本影響 |
|------|----------|
| 任何 commit 含 `BREAKING CHANGE:` 或 type 帶 `!` | **MAJOR** |
| 含 `feat` type | **MINOR** |
| 含 `fix` 或 `perf` type | **PATCH** |
| 僅 `docs` / `chore` / `style` / `refactor` / `test` / `build` / `ci` | **不觸發 bump** |

### cz changelog — 單獨生成 CHANGELOG

```bash
cz changelog          # 生成完整 CHANGELOG.md
cz changelog --dry-run  # 預覽輸出
```

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
- [ ] 若執行 `cz bump`，已確認 `--dry-run` 結果符合預期？
