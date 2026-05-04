# Changelog 與 Release 操作 Cookbook

> 本檔案是 `release-management/SKILL.md` 的操作手冊。SKILL.md 管原則與 Why；本檔案管「實際輸入哪些指令」。每段都假設讀者已理解 SKILL.md 對應 section 的紀律。

---

## 1. Hybrid CHANGELOG 6 步驟（對應 SKILL.md §2 + §3）

1. **平時**：commit 標題遵守 ≤50 char + WHY-in-body 的 conventional commits 規範，給 cz 好用的素材。

2. **Dry-run 預覽**：
   ```bash
   cz bump --changelog --dry-run
   ```

3. **正式 bump**：
   ```bash
   cz bump --changelog
   ```
   產出 scaffold 區塊（`### Feat` / `### Fix` / `### BREAKING CHANGE`），版本號 + tag 自動建立。

4. **手動潤稿**（push 前）：依 SKILL.md §3「潤稿規則」重組分類、補 WHY context、處理 BREAKING migration note。

5. **Amend 進 release commit**（潤稿在工作區是 unstaged，必須先 `git add` 否則 amend 不會納入）：
   ```bash
   git add CHANGELOG.md
   git commit --amend --no-edit
   git tag -f vX.Y.Z                    # 重新指向 amend 後的 SHA（-f 取代刪除再建）
   ```
   若 release commit 已 push 到 remote，**改走 follow-up commit**（避免改寫共享歷史）：
   ```bash
   git add CHANGELOG.md
   git commit -s -m "docs(changelog): polish vX.Y.Z entries"
   ```

6. **Push**：
   ```bash
   git push origin main --follow-tags    # --follow-tags 只推送 annotated tag，比 --tags 安全
   ```

---

## 2. PR 端寫 [Unreleased]（對應 SKILL.md §1）

每個 PR 在 merge 前，於 `CHANGELOG.md` 加：

```markdown
## [Unreleased]

### Added
- <new feature, 1-2 lines WHY>

### Changed
- <behavior change, 1-2 lines WHY>

### Fixed
- <bug fix, 1-2 lines WHY>

### Migration
- <if breaking, how downstream should adapt>
```

PR merge 後到此為止，**不要執行 `cz bump`**。

---

## 3. `pyproject.toml [tool.commitizen]` 必要設定（對應 SKILL.md §3）

```toml
[tool.commitizen]
tag_format = "v$version"                          # tag 帶 v
bump_message = "chore(release): v$new_version"    # release commit 訊息
changelog_incremental = true                      # 只 prepend 新 section，保留舊 prose
major_version_zero = true                         # pre-1.0 BREAKING bump MINOR
```

---

## 4. GitHub Release 指令（對應 SKILL.md §4）

push tag 後立刻執行：

```bash
# 從 CHANGELOG 中該版本區塊提取 notes，建立 Release
gh release create vX.Y.Z \
  --title "vX.Y.Z" \
  --notes-file <(awk '/^## \[X\.Y\.Z\]/,/^## \[/' CHANGELOG.md | sed '$d')

# 或互動式（會開編輯器，可預覽 / 微調 notes）
gh release create vX.Y.Z --notes-from-tag

# Pre-release / 不穩定版本
gh release create vX.Y.Z --prerelease
```

> 若 release notes 與 CHANGELOG 區塊內容**完全等同**，可考慮自動化（GitHub Actions on tag push）。本 skill 預設手動，因 hybrid CHANGELOG 工作流已要求人工潤稿，多走一步 `gh release create` 成本極低。
