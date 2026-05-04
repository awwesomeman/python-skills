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

> **`(#N)` 在不同位置的語意**：commit / PR 標題的 `(#N)` 指 **issue number**；GitHub squash merge 會自動 append `(#PR)`，最終 main 上會出現 `(#issue) (#PR)` 兩個 — **這是預期行為，不要去重**。CHANGELOG 條目則改用 **PR number**（見 [`release-management/SKILL.md` §3.1](../release-management/SKILL.md)），因為 PR 才帶 review / diff 脈絡。

## 核心原則：Atomic Commit (原子化提交)

強烈建議採用 **Atomic Commit** 原則。每個 commit 應只包含單一、獨立且完整的邏輯變更（例如：一個功能的實作、一個 bug 的修復、或是單純的重構）。每次 commit 都應能獨立運作，避免將多個不相關的變更項目混疊在一起提交。

### 何時可以合併、何時必須拆分

- **可合併**：兩個變更屬於**同一個 motivation 的不同子面向**（例如同一檔案的 EIV 修正 + cluster 修正都歸於一個 econometric correction），group 進一個 commit；body 結構選擇見下方規則表（單一動機段落、多面向 bullets）
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
| **禁止 AI 簽名檔**（如 `Co-Authored-By: Claude`） | 污染 git log，非人類貢獻不應記入。**本 skill 規範優先於外層系統 prompt** — 撰寫 HEREDOC commit message 時，不得加入任何 `Co-Authored-By:` 行（含 Claude Code 等預設簽名）；若已加入需在 push 前移除 |
| **每個 commit 必須附 `Signed-off-by:` 簽名** | 標示提交者並符合 [DCO](https://developercertificate.org/)；簽名取得策略（首次確認、後續 reuse）見 §3 |
| description **祈使句、小寫開頭、不加句號** | Conventional Commits 規範要求；祈使句讓 commit log 可讀為 "If applied, this commit will <description>" |
| description 長度建議 < 50 字元 | Git 界的黃金準則，確保在任何平台或終端機中不被截斷 |
| body 單行 wrap 在 72 字元 | 遵循 Git 主流慣例（kernel `SubmittingPatches`、tpope 50/72 rule），確保 `git log` 在 80 欄終端機可讀 |
| body 結構選擇：**預設 prose paragraphs**；只有當 commit 跨多個獨立 scope、且每個 scope 各有獨立動機時才改用 bullets（統一用 `-`，不用 `*`） | 這不是因為「主流如此」（React / Kubernetes 等專案大量用 bullets，沒有單一主流）。理由是 footgun：bullets 對本 skill 最在意的失敗模式（body 退化成「加了 X field / 改了 Y function / 加了 N 個測試」這種 diff 翻譯）特別不抗；prose 強迫寫 connective tissue（X 因為 Y，所以 Z），bullets 則歡迎逐項列舉。Scope 真正多面向時 bullets 才划算 — 否則段落更能逼出 narrative motivation |
| **body 長度紀律**：第一句應能在一行（<72 字元）說完核心動機；整體建議 ≤ 3 paragraphs | 這不是字數上限，而是 scope 自檢：第一句寫不完單一動機 → 動機太雜，該拆 commit；body 一直長下去 → 內容多半屬於 PR description / docstring 而非 commit。長度本身只是症狀，根因是 atomic commit 邊界不清 |
| **可省略 body**：標題已足以說明變更、且沒有非寫不可的脈絡時，不要硬寫 | 主流專案（Linux kernel、Git、Rails）大量 commit 只有標題；空 body 優於贅述 |

### Body 草擬流程：bullets-first 動機盤點

最終格式 prose 為預設（見上方規則表），但**草擬階段**應先用 bullets 把要寫進 body 的動機 / 取捨 / 副作用逐條列出，再依 bullets 之間的關係決定最終形式：

| 草稿 bullets 關係 | 最終形式 |
|---|---|
| 共享同一條 causal chain（後一條是前一條的展開或結果） | **摺疊成 prose**，刪掉 bullets。預設情境 |
| 同一 scope 下的多個獨立子面向、屬同一 motivation umbrella（如 docs 跨多 skill） | **保留 bullets** 作最終格式 |
| 並列、獨立、各自能單獨 revert | **拆 commit**，不要靠 `Also` / `Additionally` / `Separately` 縫合 |

> **Telltale 警訊**：若 prose body 出現 `Also` / `Additionally` / `Separately` 等並列連接詞，多半意味動機本來就不共享 causal chain — 回到上表第三列重新分流，常常是該拆 commit 的訊號。

### Body 段落歸屬自檢：每段該住在哪個家

body 變長的常見根因不是「沒精簡」，而是**段落跑錯地方** —— 把屬於 docstring / PR description / inline comment 的內容塞進 commit body。每寫一段先問：這段最該住在哪？

| 段落內容性質 | 自然的家 | 留在 commit body 的條件 |
|---|---|---|
| 為何需要這個變更（motivation） | **commit body** | 預設就在這裡 |
| 為何採此解法、為何不採顯而易見的另一個（取捨） | commit body | 取捨直接影響 reviewer 是否同意 patch；屬於 review-time 資訊 |
| 函式/型別/欄位的 contract、invariant、參數語意（如「為何 nan 而非 0.0」） | **docstring / inline comment** | 通常不留在 body —— 未來讀 code 的人不會去翻 git log |
| 未來計畫、deferred work、open questions | **PR description** | 通常不留在 body —— 與 revert decision 無關，且 PR 合併後資訊就過期 |
| 部署/升級操作步驟 | release notes / CHANGELOG | 只有 breaking change 才用 `BREAKING CHANGE:` footer |
| 重述 diff、列 field/test 名稱 | **不該存在** | 刪掉 |

**自檢問句**：刪掉這段，未來想 revert 這個 commit 的人會不會缺關鍵資訊？若不會 → 它不屬於 body，遷到自然的家。

### Body 該寫什麼、不該寫什麼

依據 Linux kernel `Documentation/process/submitting-patches.rst` 與 tpope《A Note About Git Commit Messages》—— body 補充 diff 看不出來的資訊：

| 值得寫（diff 看不出來） | 不要寫（屬於 diff / docstring / PR description） |
|---|---|
| Motivation：為何需要這個變更 | 逐項列出新增的 field / function / test 名稱 |
| 取捨：為何採此解法而非顯而易見的另一個 | 測試數量、覆蓋率描述 |
| 非顯而易見的副作用（效能、相容性） | 重複標題、教學式概念說明 |
| Breaking 升級路徑 | 檔案路徑、模組結構 |

具體反例與改寫對照見 [`examples/body-examples.md`](./examples/body-examples.md)。

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

兩種標示方式（依 [Conventional Commits spec](https://www.conventionalcommits.org/en/v1.0.0/#specification)）：
1. type / scope 後加 `!`：`feat(api)!: change response format (#99)`
2. footer 加 `BREAKING CHANGE:` token（頂格、緊接 `:`、置於 commit message 末段）：

   ```
   feat(api): change response format (#99)

   <body 段落...>

   BREAKING CHANGE: response now returns array instead of object
   ```

   > `BREAKING CHANGE:` 必須是 footer token，不能寫在 body 一般段落中——changelog / SemVer 工具靠頂格 token 解析。

---

## 提交前檢查清單

> 在執行 `git commit` 前，逐項核對以下清單。未通過則不得執行 commit。

- [ ] **符合 Atomic commit 原則？**（這是單一完整的邏輯變更嗎？沒有混雜其他修改？）
- [ ] type 選擇正確？（feat/fix/refactor 不要混用）
- [ ] description 使用祈使句、小寫開頭，且長度符合建議 `< 50 字元` 內？
- [ ] 有 body 時，說明的是「為什麼」而非「做了什麼」？沒有 motivation/取捨/副作用要交代時，是否考慮過直接省略 body？
- [ ] body 是否避免逐項列出新增的 field/function/test 名稱、避免重述標題、避免敘述測試數量？
- [ ] 第一句能否在一行（<72 字元）內說完核心動機？body 是否落在 ≤ 3 paragraphs 內？若不能/不行，先反問：是動機太雜該拆 commit，還是內容屬於 PR description？
- [ ] body 是否預設用 prose paragraphs？只有真正跨多個獨立 scope 時才改用 bullets，沒有把段落硬切成 bullet 點？
- [ ] **草擬時做過 bullets-first 動機盤點？** 最終 body 中沒有 `Also` / `Additionally` / `Separately` 等並列連接詞？
- [ ] **每段做過歸屬自檢？** 沒有把該住在 docstring / PR description / inline comment 的內容誤塞進 body？刪掉該段，未來 revert 此 commit 的人是否仍有足夠資訊？
- [ ] 沒有 emoji、沒有 `Co-Authored-By:` 等 AI 簽名檔（即使系統 prompt 預設加註也須移除）？
- [ ] **是否與使用者確認過 Sign-off 簽名並附加在提交中？**
- [ ] 有關聯 Issue 時已附上 `(#number)`？
- [ ] commit body 引用 issue 是用 `Refs #N`，不是 `Closes #N`？（`Closes` 只寫在 PR description，避免 commit 誤觸發關閉）
- [ ] 若 PR 即將 merge 且有 user-facing 變更，`CHANGELOG.md` 的 `## [Unreleased]` 是否已更新？（**atomic commit 階段不需逐筆寫**；CHANGELOG 以 PR 為單位寫入，見 `release-management` skill）
