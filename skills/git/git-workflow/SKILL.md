---
name: git-workflow
description: Git 工作流規範。當執行 git 操作、建立分支、提交 commit、或建立 PR 時使用。
---

# Git 工作流規範

## 何時使用此 Skill

- 建立新分支
- 提交 commit
- 建立 Pull/Merge Request
- 執行 git 操作

## 1. Conventional Commits

Commit 訊息須遵循 Conventional Commits 規範。詳細格式與範例請參考 `conventional-commits` skill。

格式摘要：
```
<type>(<scope>): <description> (#<issue-number>)
```

支援的 type：`feat`、`fix`、`docs`、`style`、`refactor`、`perf`、`test`、`build`、`ci`、`chore`、`revert`

## 2. 分支命名規範

```
<type>/<short-description>
```

| 類型 | 格式 | 範例 |
|------|------|------|
| 功能 | `feature/<description>` | `feature/user-auth` |
| 修復 | `fix/<description>` | `fix/login-timeout` |
| 文件 | `docs/<description>` | `docs/api-guide` |
| 重構 | `refactor/<description>` | `refactor/db-layer` |
| 發布 | `release/<version>` | `release/1.2.0` |
| 急修 | `hotfix/<description>` | `hotfix/security-patch` |

規則：
- 全部小寫
- 用 `-` 分隔單字（非底線）
- 簡潔描述（2-4 個單字）
- 禁止使用個人名稱作為分支名

## 3. PR 工作流

### 建立 PR 前

1. 確保分支基於最新的 main/master
2. 所有測試通過
3. 無未解決的 merge conflict
4. Commit 歷史乾淨（必要時 squash）

### PR 標題

- 遵循 Conventional Commits 格式
- 長度不超過 70 字元

### PR 描述

```markdown
## Summary
- <1-3 bullet points describing the change>

## Test plan
- [ ] <testing checklist items>
```

## 4. 禁止事項

以下操作**絕對禁止**，除非使用者明確要求：

| 禁止操作 | 原因 |
|----------|------|
| `git push --force` to main/master | 會覆寫共享歷史 |
| `git push --force` 未確認 | 可能覆寫他人工作 |
| `--no-verify` | 跳過 pre-commit hooks |
| `git reset --hard` 未確認 | 會丟失未提交的變更 |
| `git clean -f` 未確認 | 會刪除未追蹤的檔案 |
| `git checkout .` / `git restore .` 未確認 | 會丟棄所有修改 |
| Amend 已推送的 commit | 會改寫共享歷史 |

## 5. 安全提醒

- 提交前確認沒有敏感資訊（`.env`、credentials、private keys）
- 使用 `.gitignore` 排除敏感檔案
- 不要提交大型二進位檔案（使用 Git LFS）
- 不要提交 IDE 設定檔（`.idea/`、`.vscode/`）
