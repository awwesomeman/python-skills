# Commit Body 反例與改寫

> 參考檔案。SKILL.md 規則的具體示範，幫助 agent 看出「重述 diff vs 補充 motivation」的差異。

## 原則回顧

body 補充 diff 看不出來的資訊（motivation、取捨、副作用、breaking 升級路徑）。
不重述 diff、不列 field/test 數量、不重複標題、不寫教學說明、不報路徑。

沒有非寫不可的脈絡 → 直接省略 body（主流專案 Linux kernel、Git、Rails 大量 commit 只有標題）。

---

## 反例（重述 diff、列出實作細節）

```
feat(introspect): SuggestConfigResult.detected

Add structured panel observations behind the suggestion. Same
data the reasoning strings narrate, but machine-readable for AI
agents / pipeline gates that branch programmatically.

- New field SuggestConfigResult.detected: dict[str, Any] with 7
  type-stable keys (scope, signal, mode, n_assets, ...).
- _detect_signal now returns sparsity (was computed but discarded).
- Module-level DETECTED_KEYS frozenset in _describe.py serves as SSOT.
- 6 boundary tests in tests/test_introspection.py covering ...
- alternatives: list[AnalysisConfig] deliberately deferred — semantics
  need real user feedback before locking the contract.

Refs #20
```

問題：
- 標題重複（"SuggestConfigResult.detected" → body 又寫一次）
- 列出 dict key 名、檔名、test 數量 — 全是 diff 已呈現的資訊
- 解釋 `DETECTED_KEYS` 為何是 SSOT — 屬於 docstring

## 正例（只留 motivation 與刻意取捨）

```
feat(introspect): expose machine-readable detection result

Reasoning strings are useful for humans but not for pipeline
gates that branch on panel shape. Surface the same observations
as a structured dict so downstream agents don't need to parse
prose.

The companion `alternatives` field from the original sketch is
deferred — its contract needs real user feedback before locking.

Refs #20
```

保留的資訊：
- **Motivation**：為何需要這個結構化欄位（pipeline gates 不該 parse prose）
- **取捨**：為何 `alternatives` 不一起做（contract 未穩定）
- **追蹤連結**：`Refs #20`（commit body 用 `Refs`，避免提前關閉；`Closes` 留給 PR description）

捨棄的資訊（diff 已涵蓋）：dict 的 key 名、test 數量、SSOT 實作細節。

---

## 何時用列點：跨多檔/多 skill 的 commit

單一動機的 commit 用段落即可（如上例）。當 commit 跨多個檔案/模組、每個檔案各自有獨立的小動機時，用 scope-level bullets 讓讀者快速掃出影響面。

### 正例（每條 bullet = 一個 scope，不是逐項列 diff）

```
docs(git): tighten commit/changelog/doc responsibility rules

Cross-skill rules were inconsistent on where each piece of
information lives, and the Refs/Closes split lacked a single source.

- parent skill: add 文件權責矩陣 as the canonical mapping
- conventional-commits: tighten body rules against kernel guide
- git-workflow: drop redundant Closes #N from squash template
- release-management: add §3.1 entry rules + bad/good examples
```

每條 bullet 描述「該 scope 改了什麼層級的東西」與「為何」，**不展開到 field/function/test 名稱**——後者屬於 diff。

### 反例（bullet 內塞 diff 細節）

```
- parent skill: added a markdown table at line 38 with 10 rows including
  "What 變了", "Why 變了", "Issue / PR 追蹤連結" columns covering...
```

bullet 退化成 diff 的文字版，失去 scope-level 摘要的意義。
