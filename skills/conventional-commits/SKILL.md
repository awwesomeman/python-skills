---
name: conventional-commits
description: 建立遵循 Conventional Commits 規範的 git commit，自動分析變更內容、生成標準化訊息，並附上 Issue Number 和 Signed-off-by 簽名。
---

# Conventional Commit Skill

這個 Skill 用於建立符合 [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) 規範的 git commit。

## Commit Message 格式

```
<type>(<scope>): <description> (#<issue-number>)

[optional body]
```

## 重要規則

- **禁止加入任何 emoji**
- **禁止加入 Claude 或 AI 相關的簽名檔**（如 Co-Authored-By: Claude）
- **禁止手動撰寫或假設用戶的 name 和 email**
- description 使用小寫開頭，結尾不加句號
- 保持 description 簡潔（建議 50 字元以內）
- body 只寫必要資訊，保持乾淨簡潔

## 支援的 Type 類型

| Type | 說明 |
|------|------|
| `feat` | 新增功能 (對應 SemVer MINOR) |
| `fix` | 修復 bug (對應 SemVer PATCH) |
| `docs` | 文件變更 |
| `style` | 程式碼格式調整 (不影響邏輯) |
| `refactor` | 重構程式碼 (不新增功能或修復 bug) |
| `perf` | 效能優化 |
| `test` | 新增或修改測試 |
| `build` | 建置系統或外部依賴變更 |
| `ci` | CI 設定變更 |
| `chore` | 其他維護性變更 |
| `revert` | 還原先前的 commit |

## 執行步驟

當用戶請求 commit 時，依照以下步驟執行：

### 1. 檢查 Git 狀態

執行以下指令確認目前狀態：

```bash
git status
git diff --staged
git diff
```

### 2. 分析變更內容

根據變更的檔案和內容判斷：
- **type**: 根據變更性質選擇適當的類型
- **scope**: 根據變更的模組或功能區域決定 (可選)
- **description**: 簡潔描述變更內容，使用祈使句 (imperative mood)

### 3. 詢問 Issue Number

**重要**：使用 AskUserQuestion 工具詢問用戶關聯的 Issue Number。

詢問範例：
- 「請問這個 commit 關聯的 Issue Number 是什麼？（如無則可留空）」

如果用戶提供 Issue Number，則在 commit message 結尾加上 `(#<issue-number>)`。
如果用戶表示沒有關聯的 Issue，則省略此部分。

### 4. 生成 Commit Message

組合成符合規範的訊息格式：

**有 Issue Number：**
```
<type>(<scope>): <description> (#<issue-number>)
```

**無 Issue Number：**
```
<type>(<scope>): <description>
```

範例：
- `docs(readme): update installation guide (#1)`
- `feat(plugin): add new data source connector (#2)`
- `fix(auth): resolve token expiration issue (#123)`
- `refactor(api): simplify error handling logic`

### 5. 撰寫 Body（可選）

當變更較複雜或需要額外說明時，加入 body 區塊。

**Body 撰寫原則：**
- 簡潔扼要，只寫必要資訊
- 說明「為什麼」做這個變更，而非「做了什麼」（標題已說明）
- 條列式呈現多項變更
- 保持乾淨，不加冗詞贅字

**Body 範例：**

```
feat(auth): add OAuth2 login support (#45)

- Add Google and GitHub OAuth providers
- Store refresh tokens in secure cookie
- Auto-redirect after successful login
```

```
fix(api): resolve memory leak in connection pool (#78)

Connection was not properly released when request timeout.
Added finally block to ensure cleanup.
```

### 6. 執行 Commit

使用 `-s` 參數讓 git 自動附上 Signed-off-by 簽名。

**關於 `-s` 參數**：git 會自動從 `git config user.name` 和 `git config user.email` 讀取用戶資訊，不需要也不應該手動撰寫 `Signed-off-by` 行。

**簡單 commit（僅標題）：**
```bash
git add <files>  # 如果需要
git commit -s -m "<commit-message>"
```

**含 body 的 commit：**
```bash
git commit -s -m "<title>" -m "<body>"
```

或使用 heredoc 格式：
```bash
git commit -s -m "$(cat <<'EOF'
<title>

<body>
EOF
)"
```

## 破壞性變更 (Breaking Changes)

如果是破壞性變更，有兩種標示方式：

1. 在 type 後加驚嘆號，例如：`feat(api)!: change response format (#99)`

2. 在 body 中說明，加入 `BREAKING CHANGE:` 前綴：
   - 標題：`feat(api): change response format (#99)`
   - Body：`BREAKING CHANGE: response now returns array instead of object`
