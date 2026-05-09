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
   git tag -fa vX.Y.Z -m "vX.Y.Z"       # -a 必加！cz 原 tag 是 annotated，
                                        # 純 `-f` 會降級為 lightweight，
                                        # 下一步 `--follow-tags` 就不會推
   ```
   若 release commit 已 push 到 remote，**改走 follow-up commit**（避免改寫共享歷史）：
   ```bash
   git add CHANGELOG.md
   git commit -s -m "docs(changelog): polish vX.Y.Z entries"
   ```

6. **Push**：
   ```bash
   git push origin main --follow-tags    # 只推 annotated tag（lightweight 會被忽略）；
                                         # 若 push 後發現 tag 沒上 remote，
                                         # 99% 是上一步漏了 `-a` 變成 lightweight
   ```

---

## 2. PR 端寫 [Unreleased]（對應 SKILL.md §1、§3.1）

### 2.1 區塊模板

每個 PR 在 merge 前，於 `CHANGELOG.md` 加：

```markdown
## [Unreleased]

### Added
- <user-facing 變更> — <WHY / 影響>. (#PR)

### Changed
- <behavior change> — <WHY>. (#PR)

### Fixed
- <bug fix> — <觸發條件 or 修復後行為>. (#PR)

### Removed
- <breaking 變更>，改用 X / 將 Y 設為 Z. (#PR)
```

PR merge 後到此為止，**不要執行 `cz bump`**。

> 撰寫原則見 SKILL.md §3.1，本節只示範模板與反/正例對照。

### 2.2 反例與正例對照

**反例**（直貼 commit title、缺 WHY、缺 migration、列實作細節）：

```markdown
### Added
- feat(introspect): SuggestConfigResult.detected
- feat(introspect): add structured panel observations dict with 7 type-stable
  keys including scope, signal, mode, n_assets, n_periods, sparsity, and
  magnitude_dropped, plus 6 boundary tests in tests/test_introspection.py

### Removed
- BREAKING CHANGE: response format changed
```

**正例**（user 視角、有 WHY、有 migration、有連結）：

```markdown
### Added
- expose `SuggestConfigResult.detected` dict — lets pipeline gates branch on
  panel shape without parsing reasoning strings. (#20)

### Removed
- `analyze()` now returns an iterator instead of a list — wrap the call in
  `list(...)` if you relied on indexing or `len()`. (#34)
```

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

> Push tag **前**先判斷 Mode：`ls .github/workflows/ | xargs grep -l "tags:.*v\\*"` 找有沒有 tag-triggered release workflow。

### 4.1 Mode A — 手動建 Release

無 tag-triggered CI release workflow 時，push tag 後立刻執行：

```bash
# 從 CHANGELOG 中該版本區塊提取 notes，建立 Release
# heading 對齊 cz 預設模板 `## v$version`（見 SKILL.md §5）
gh release create vX.Y.Z \
  --title "vX.Y.Z" \
  --latest \
  --notes-file <(awk '/^## vX\.Y\.Z/,/^## v/' CHANGELOG.md | sed '$d')

# 或互動式（會開編輯器，可預覽 / 微調 notes）
gh release create vX.Y.Z --notes-from-tag

# Pre-release / 不穩定版本
gh release create vX.Y.Z --prerelease
```

### 4.2 Mode B — CI 自動建 Release，只做驗證

有 tag-triggered workflow（典型結構：`build` → `publish` PyPI → `github-release` with dist artifacts）時，push 完 tag **不要手動 `gh release create`**。等 CI 跑完再驗證：

```bash
# 等 CI 完成
gh run watch $(gh run list --workflow=release.yml --limit=1 --json databaseId --jq '.[0].databaseId')

# 驗證 Release page + dist 附件齊全
gh release view vX.Y.Z --json tagName,name,isDraft,isPrerelease,assets \
  --jq '{tagName, name, isDraft, isPrerelease, assets: [.assets[].name]}'
# 期望輸出包含 .whl + .tar.gz（Python 套件）或對應語言的 artifacts
```

### 4.3 Mode B 失敗恢復

CI release workflow fail 時的標準恢復腳本：

```bash
RUN_ID=$(gh run list --workflow=release.yml --limit=1 --json databaseId --jq '.[0].databaseId')

# Step 1: 確認哪個 sub-job 失敗 + publish 是否成功
gh run view "$RUN_ID" --json jobs --jq '.jobs[] | {name, conclusion}'

# Step 2: 若 github-release fail（最常見：race condition / CHANGELOG regex mismatch）
#         且 publish=success → PyPI 已上線、不可重 publish
gh release delete vX.Y.Z --yes        # 保留 tag，只刪 Release page
gh run rerun "$RUN_ID" --failed       # 只重跑失敗 job，build/publish 不重跑

# Step 3: 等重跑完成 + 驗證
gh run watch "$RUN_ID"
gh release view vX.Y.Z --json assets --jq '[.assets[].name]'
```

常見的 CI 自製 idempotency guard（會 trip 到第一次 fail 的就是這個 step）：

```yaml
# .github/workflows/release.yml
- name: Fail if release already exists
  env:
    GH_TOKEN: ${{ github.token }}
  run: |
    TAG="${GITHUB_REF#refs/tags/}"
    if gh release view "$TAG" &>/dev/null; then
      echo "Release $TAG already exists — refusing to overwrite" >&2
      exit 1
    fi
```

設計用意是**防止 workflow 自己被重觸發兩次**而覆蓋既有 Release；但會誤殺「人類在 CI 之前手動 `gh release create`」的場景——這也是 Mode B 不該手動建 Release 的核心原因。

### Don't

- Mode B 下用 `gh run rerun --failed` 之前**沒先 `gh release delete`** — guard step 還是會 fail，rerun 變空轉
- Mode B 下「為了趕快 ship」手動 `gh release create` —— 看似快，卻換來 (a) CI 紅燈 (b) Release page 沒附件 (c) 還是要走恢復流程，總時間更長
- 用 `git tag -d vX.Y.Z && git push --delete origin vX.Y.Z && git tag vX.Y.Z && git push --tags` 重觸發 workflow——這會搞亂 tag 歷史；正確做法是 `gh run rerun --failed`，tag 不動
