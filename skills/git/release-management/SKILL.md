---
name: release-management
description: 版本發布節奏與機制。當判斷是否要 release、執行 cz bump、撰寫 CHANGELOG、建立 GitHub Release、或查 SemVer / 版本命名規則時使用。涵蓋 release-train 節奏、bump 位置紀律、hybrid changelog 工作流、GitHub Release、版本命名一致性、SemVer bump 速查。
---

# Release Management Skill

處理「**release 節奏**」（何時 bump）與「**release 機制**」（在哪 bump、怎麼 bump、如何寫 CHANGELOG、如何發 GitHub Release）兩個層次。

> **工具選擇**：本 skill 以 [Commitizen](https://commitizen-tools.github.io/commitizen/) (`cz`) 作為 bump / changelog 的標準工具——它會解析 Conventional Commits 自動推導 SemVer 等級、更新版本檔案、產生 changelog scaffold、打 tag，是目前 Python 生態最成熟的選擇。其他等價工具（semantic-release、release-please、changesets）原則相通，但本 skill 的指令範例、`pyproject.toml` 設定皆以 `cz` 為基準；若改用其他工具請對應替換。
>
> 所有操作指令（6 步驟流程、`pyproject.toml` 設定、`gh release create` 範例）皆在 [`examples/changelog-workflow.md`](./examples/changelog-workflow.md)。本 SKILL.md 只談原則與 Why。

---

## 1. Release-Train 節奏（何時 bump）

> 核心原則：**PR merge 不觸發 `cz bump`**。版本 + tag 只在累積到 milestone 時才推一次。

### Why（拒絕「每 PR bump」的副作用）

- 版本號膨脹失真（4 個小 PR → 4 個 minor versions），讓版本號失去傳遞「這次有重大改變」的訊號
- CHANGELOG 變成片段化條列，narrative 連貫性消失
- 下游收到大量 bump 通知，無法分辨哪些版本真的需要關注

### How to apply

- **PR 端**：每個 PR 只負責寫入 `CHANGELOG.md` 的 `## [Unreleased]` 區塊（依 Keep a Changelog 分類），merge 後到此為止——**不要執行 `cz bump`**。模板見 [examples §3](./examples/changelog-workflow.md)。
- **Release 端觸發條件**：以下任一成立才執行 `cz bump --changelog`：

| 觸發條件 | 說明 |
|---------|------|
| ≥ 3 個 user-facing `feat:` / `fix:` 累積 | 累積到一個有意義的版本 |
| ≥ 2 週未 tag 且至少 1 個 user-facing 變更 | 避免 `[Unreleased]` 無限堆積 |
| 下游專案（含 monorepo workspace 成員）急需 bug fix | 單一 PATCH OK |
| 需要命名版本給 demo / pin 使用 | 即時切版 |

> 若不確定是否要 release，**預設「等」**——多累積一週的成本接近零；過早 release 的版本號永遠留在 tag 歷史。

---

## 2. Bump 位置紀律：只在 main 上 bump

> **`cz bump` 與建立版本 tag 一律在 `main` 分支執行，禁止在 feature branch 上跑。**

### Why

- Tag 落在 branch SHA，`main` 還看不到
- 多輪迭代會產生多個從未 ship 的 release tag，collapsing 回單一版本要 force-push branch、刪 remote tag、retag、force-push main——恢復成本極高
- PR description 跨多個 "release"，但這些 release 對 consumer 都不存在

即使是「pre-1.0、單作者」場景仍適用——cost of error 不對稱。

### How to apply

- **Feature branch 端**：只放 `feat` / `fix` / `refactor!` 等 commits，維持正確的 `!` 紀律讓 cz 之後能推導 bump level。
- **Main 端**：完整 bump → 潤稿 → amend → push 流程見 [examples §1](./examples/changelog-workflow.md)。

---

## 3. Hybrid CHANGELOG 工作流（cz scaffold + 手動潤稿）

> **既不純手寫，也不純 `cz bump --changelog` 自動生成。** 用 cz 產出 scaffold，再手動補 WHY 與 Keep-a-Changelog 結構。

### Why

- **純手寫**：慢且容易遺漏（曾經 ship 過 0.2.0 完全沒寫 CHANGELOG section、0.3.0 差點貼到 0.2.0 的內容）
- **純 `cz bump --changelog`**：把 commit titles 列在 `### Feat` / `### Fix` 下面，遺失多行 WHY context；對於 methodology / academic-leaning 專案，CHANGELOG 應承載「為什麼這個變了」，不只是 commit title 清單

Hybrid 拿 cz scaffold 當 safety net（catch missing entries），再手動補 narrative。

### How to apply

6 步驟流程（dry-run → bump → 潤稿 → amend → push）見 [examples §1](./examples/changelog-workflow.md)。`pyproject.toml [tool.commitizen]` 必要設定見 [examples §3](./examples/changelog-workflow.md)。

潤稿規則（單一資料源）：

- cz 分類重組為 Keep a Changelog 風格：`### Feat` → `### Added`、`### Fix` → `### Fixed`、`### Refactor` → `### Changed`、內部 docs → `### Docs`
- `feat!` / `BREAKING CHANGE:` 條目移到獨立的 `### Removed`，加 1 行 migration note
- 每個 material entry 加 1-2 行 WHY context（motivation、citation、scope）

### 3.1 Entry 撰寫原則

> 目標：**簡單但保留追蹤所需的關鍵資訊**。讀者是「想升級這個版本卻不知會不會壞掉」的下游開發者。

每個 entry 結構：`- <user-facing 變更> — <WHY / 影響>. (#PR)`

| 規則 | 為什麼 |
|------|--------|
| user / API consumer 視角，非實作視角 | 下游 skim changelog 是為了判斷影響面，不是 review code |
| Breaking / Removed entry 永遠附 migration note | 「改用 X」「將 Y 設為 Z」是升級時最常被搜尋的關鍵字 |
| 不直貼 commit title、不列檔名/函式名/test 數量 | commit title 缺 WHY；實作細節屬 PR description |
| 同模組多個 fix 合併為一條 | 避免 fragmentation；下游關心模組級影響 |
| 動詞短語或陳述句皆可，不強制祈使句 | 對齊 [Keep a Changelog](https://keepachangelog.com/) 主流範例（"Added X" / "New visual identity" 混用） |
| 連結用 **PR number** 而非 issue number（與 commit 標題的 `(#issue)` 不同） | PR 帶 diff、review、討論脈絡，是下游追問題的正確入口；issue 只描述需求，缺實作細節 |
| Keep a Changelog 標準分類僅 `Added / Changed / Deprecated / Removed / Fixed / Security` | Migration 不是合法 section；migration note 寫進 `Removed` / `Changed` 條目本身 |

模板與反例/正例對照見 [examples §2](./examples/changelog-workflow.md)。

### Don't

- 跑完 `cz bump --changelog` 直接 push，跳過手動潤稿（會永久 ship bare scaffold）
- `cz bump` 不帶 `--changelog`，再另開 commit 手寫（這是「容易忘記寫」的舊流程）
- 把 `changelog_incremental = false`（會在下次 bump 把過去手寫的舊版內容洗掉）

---

## 4. GitHub Release Page

> **`git push --tags` 不等於 release**。tag 是 git 物件，Release 是 GitHub 上對外可見的 page（含 release notes、artifacts、RSS、API endpoint）。下游 / 使用者 / dependabot 看的是 Release，不是 tag。

### Why

| 只 push tag、不開 Release | 結果 |
|---------------------------|------|
| 使用者 watch repo 收到 release 通知 | 不會收到（GitHub 只在 Release publish 時通知） |
| 套件管理工具（uv、pip、cargo 等）解析版本 | 多數仍能用 tag，但 release notes 不可見 |
| 下游需要 changelog 連結 | 必須點進 raw `CHANGELOG.md`，UX 差 |
| API consumers 拉取 release metadata | `/releases/latest` 回 404 |

### How to apply

push tag 後**立刻** `gh release create vX.Y.Z`，notes 取自 CHANGELOG 該版本區塊。完整指令（`--notes-file` / `--notes-from-tag` / `--prerelease` 變體）見 [examples §4](./examples/changelog-workflow.md)。

### Don't

- 推完 tag 就停手（沒人看得到 release）
- Release notes 直接貼整份 CHANGELOG（應只貼該版本區塊）
- 在 GitHub UI 手動建立卻不對齊 tag（Release 與 tag 脫鉤）

---

## 5. 版本命名一致性

| 位置 | 格式 | 為什麼 |
|------|------|--------|
| **Git Tag** | `v1.2.3` | 帶 `v` 前綴，方便 git refs 識別 |
| **CHANGELOG.md** | `## [1.2.3]` | **不**帶 `v` 前綴，符合 SemVer 純數字定義 |
| **Commit Message** | `chore(release): v1.2.3` | 帶 `v` 前綴，明確標記 release |

---

## 6. SemVer Bump 觸發規則速查

| 條件 | 版本影響 |
|------|----------|
| 任何 commit 含 `BREAKING CHANGE:` 或 type 帶 `!` | **MAJOR**（pre-1.0 為 MINOR） |
| 含 `feat` type | **MINOR** |
| 含 `fix` 或 `perf` type | **PATCH** |
| 含 `revert` type | 視被 revert 的原 commit type 而定（revert 一個 `feat` → MINOR；revert 一個 `fix` → PATCH） |
| 僅 `docs` / `chore` / `style` / `refactor` / `test` / `build` / `ci` | **不觸發 bump** |

> **Pre-1.0 (0.y.z)**：依 SemVer，1.0.0 之前 API 尚未穩定，MINOR 變動通常被視為 Breaking。專案初期可以靠 `major_version_zero = true` 自動把 BREAKING 降級為 MINOR bump。

---

## 7. Release 前檢查清單

> 觸發 `cz bump --changelog` 前逐項核對。

- [ ] 目前在 `main` 分支且 `git pull` 已同步？
- [ ] 累積變更達到 release-train 觸發條件（≥3 user-facing / ≥2 週 / 急修 / 命名需求）？
- [ ] 所有測試通過、Lint 無誤？
- [ ] `cz bump --changelog --dry-run` 顯示的 bump level 正確？
- [ ] `[Unreleased]` 區塊內容已準備好被 release？

> Push 前再核對：

- [ ] CHANGELOG 的 cz scaffold 已手動潤稿（Keep-a-Changelog 結構、WHY context、Removed migration note）？
- [ ] 潤稿已 amend 進 release commit、tag 已重新指向 amend 後 SHA？
- [ ] `git push origin main --follow-tags` 已準備（**不要漏 tag**；偏好 `--follow-tags` 而非 `--tags`，前者只推送已關聯 commit 的 annotated tag，避免誤推本地殘留 tag）？

> Push 後再核對：

- [ ] **已建立 GitHub Release** (`gh release create vX.Y.Z`) 並貼上該版本的 release notes？（push tag ≠ release）
- [ ] 下游專案（含 monorepo workspace 成員）是否需要同步 pin？
