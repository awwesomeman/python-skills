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

---

## 反例：`Also` connective = 動機混雜的訊號

當 prose body 必須用 `Also` / `Additionally` / `Separately` 把段落縫起來，多半意味動機本來就不共享 causal chain。應拆 commit 或重新組織敘事，不要靠連接詞遮蓋。

### 反例（用 `Also` 把獨立動機強縫成 prose）

```
docs(conventional-commits): reground body rules

Previous body rules cited "mainstream practice" — selective sampling.
Reground the prose-default rule in the actual concern: bullets are
a footgun for the WHAT-list failure mode this skill already forbids.

Add a length-discipline rule on the same basis — first sentence in
one line, ≤ 3 paragraphs — framed as scope self-check.

Also fix line 26's internal contradiction (boundary "identical" yet
needing bullets is self-defeating): reword to "same motivation,
distinct sub-aspects".
```

問題：第三段 `Also fix line 26...` 是 telltale —— 前兩段共享 causal chain（同一個 reground 動機），第三段是另一條獨立關注（內部一致性），用 `Also` 強縫只是把問題藏起來。

### 改寫一：把 line 26 修正當作同一 review pass 的延續，用 causal continuation

```
docs(conventional-commits): reground body rules in internal logic

Earlier wording justified prose-default and length limits by appeal
to "mainstream practice", which is selective sampling. Replace that
justification with the actual concern: bullets are a footgun for
the WHAT-list failure mode this skill already forbids, and oversized
bodies are a scope smell rather than a word-count violation. The
same review pass surfaces a downstream wording slip on the merge-
case entry — "boundaries 完全相同" yet recommending bullets —
reworded here to "same motivation, distinct sub-aspects".
```

`The same review pass surfaces...` 是 causal continuation，不是並列縫合 —— 措辭修正自然從前文的「重新審視論證」帶出。

### 改寫二（如果 line 26 修正真的獨立到無法 causal continue）

拆兩個 commit，不要硬縫。

---

## 反例：段落跑錯家（屬於 docstring / PR description）

body 變長常因為段落該住在別的家。每段做歸屬自檢：未來讀 code 的人會去 docstring 還是 git log 找這資訊？

### 反例（取捨段屬 docstring、計畫段屬 PR description）

```
feat(introspect): SuggestConfigResult.detected (#20)

Surface the structured panel observations that drove a suggestion
so AI agents and pipeline gates can branch programmatically. The
information was already computed inside suggest_config and thrown
away; consumers had to either parse the reasoning narrative
strings or re-derive the observations from the raw panel.

Why nan (not 0.0) for empty-panel sparsity: a zero-ratio is
undefined when there are no observations. Reporting 0.0 would
falsely imply 'fully dense' and consumers branching on
sparsity == 0 would mis-classify empty input.

The original #9 R6 sketch also proposed alternatives:
list[AnalysisConfig]. Deferred — the semantics of 'neighbouring
config' (axis-flip vs threshold-borderline vs domain-equivalent)
are speculative without real user feedback.

Refs #20
```

歸屬自檢：

| 段 | 內容性質 | 自然的家 | 該留嗎 |
|---|---|---|---|
| §1 | motivation | commit body | ✓ 留 |
| §2 | API contract（為何 nan）| **docstring** | 遷出 — 未來讀 `SuggestConfigResult` 的人會看 docstring，不會翻 git log |
| §3 | deferred work / planning | **PR description** | 遷出 — 與 revert decision 無關，PR 合併後資訊也過期 |

### 改寫（只留 motivation 段，其他遷家）

```
feat(introspect): expose machine-readable detection result (#20)

Reasoning strings are useful for humans but not for pipeline gates
that branch on panel shape. Surface the same observations as a
structured dict so downstream agents don't need to parse prose.

Refs #20
```

- §2 移到 `SuggestConfigResult.sparsity` 的 docstring（"empty panel returns nan because zero-ratio is undefined ..."）
- §3 移到 PR description 的 "Deferred / Out of scope" 區塊
- body 從 3 段壓到 1 段，但**沒有壓縮資訊** —— 資訊只是搬到正確的家

自檢問句驗證：刪掉 §2/§3 後，未來想 revert 這個 commit 的人是否仍有足夠資訊？是 —— 因為 docstring 與 PR description 仍在原處可查。

---

## 反例：複製 issue body 的 Scope / Expected / DoD 進 commit body

當 PR 對應的 issue 已寫過 `## Scope` / `## Expected` / `## Definition of Done`，commit body 不該複製貼上 —— issue 是 single source，複製只會 rot：issue body 後續編輯不會傳播到 commit。

### 反例（commit body 整段抄 issue）

```
refactor(metrics): split four-angle primitives (#48)

## Scope
- Move IC / IR / turnover / decay primitives out of metrics.py
- Each primitive owns its own module under metrics/

## Expected
- Public API unchanged; imports from factrix.metrics keep working
- Each module ≤ 200 LOC

## Definition of Done
- [x] All primitives have isolated test files
- [x] mypy --strict passes
- [x] No circular imports

Refs #48
```

問題：三個段落全部從 issue #48 body 複製，commit body 變成 issue 的鏡像。Issue 是契約 / spec 的 single source；commit body 該補的是「**為何這次選擇這樣切**」的 diff-invisible why。

### 改寫（只留 diff-invisible 的 motivation）

```
refactor(metrics): split four-angle primitives into modules (#48)

metrics.py grew past the point where four unrelated primitives
shared a file out of historical accident. Splitting now (before
adding the fifth in #52) keeps the import surface stable while
letting each primitive evolve independently — the alternative
of waiting until #52 forces the split would mix mechanical move
with new logic in one diff.

Refs #48
```

留下的是 issue body 不會寫的 why：「為何**現在**切，而不是等 #52」 —— 這是 reviewer 在 PR 階段、或未來 `git blame` 時會想知道的取捨，不重複 spec / DoD。

---

## 反例：列出檔案重命名 / 目錄樹

`git show` / PR Files tab 已逐檔顯示 rename，commit body 再列一次純粹是雜訊。

### 反例

```
refactor(layout): reorganise metrics package

Move the four primitives into a flat module layout under
factrix/metrics/.

Files moved:
- src/factrix/metrics.py → src/factrix/metrics/__init__.py
- src/factrix/_ic_impl.py → src/factrix/metrics/ic.py
- src/factrix/_ir_impl.py → src/factrix/metrics/ir.py
- src/factrix/_turnover_impl.py → src/factrix/metrics/turnover.py
- src/factrix/_decay_impl.py → src/factrix/metrics/decay.py

Tree after:
  factrix/metrics/
    __init__.py
    ic.py
    ir.py
    turnover.py
    decay.py
```

問題：rename 清單與目錄樹 100% 是 diff 已呈現的資訊；body 沒有任何 motivation。

### 改寫（省略 body 或只留 why）

機械化 rename + 無語意變更 → **直接省略 body**：

```
refactor(layout): flatten metrics package layout
```

若有取捨值得記（例如「為何不直接拆 sub-package」），才寫一兩行 motivation —— 但仍不列檔案清單。
