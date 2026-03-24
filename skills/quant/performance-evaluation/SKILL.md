---
name: quant-performance-evaluation
description: Standards and pitfalls for performance calculation, risk metrics, factor evaluation, and turnover analysis. Use when analyzing strategy results, calculating metrics, or evaluating factor quality.
pipeline_layer: "Stats Layer (Pandas/NumPy/SciPy)"
---

# 績效計算與回測指標 (Performance Metrics)

> Agent 本身會計算 Sharpe、MDD 等指標。本 skill 的價值在於指出**哪些常見寫法是錯的**。接收 `execution-simulation` 的淨報酬序列，結果可送入 `multiple-testing` 或 `regime-analysis` 做進一步檢驗。

---

## 1. 年化與收益率（通用）

- 年化係數（252 交易日、365 加密貨幣）必須集中定義在 config，不可散落為魔術數字
- 累積淨值用 `(1 + returns).cumprod()`，起點為 1
- 年化報酬用幾何法：`(1 + r).prod() ** (252 / n_days) - 1`

---

## 2. 核心指標陷阱（通用）

### Sharpe Ratio
- **ddof 必須全專案統一**：`ddof=1`（樣本標準差，業界主流）或 `ddof=0`（母體，理論推導）。混用會導致跨策略比較產生系統性偏差
- **無風險利率不可用常數**：10 年回測中 Rf 從 0% 到 5% 劇烈波動，應傳入與 returns 對齊的 Rf Series
- **自相關膨脹**：日頻策略的 SR 常因報酬自相關而膨脹 30%+（Lo, 2002），均值回歸策略尤其嚴重

### MDD
- 用 `cumprod` 算淨值 → `cummax` 算歷史高點 → `(wealth - peak) / peak`
- 回傳正數或負數需在專案內統一
- **最長水下天數 (Drawdown Duration)** 比 MDD 深度更重要，資產管理極度重視

### Sortino Ratio
🚨 分母必須用**全樣本長度**算下行標準差，不可只除以負報酬天數。公式：`sqrt(mean(min(r - MAR, 0)²)) × sqrt(252)`

### Calmar Ratio
年化報酬 / MDD。MDD 為零時回傳 NaN，不可回傳 Infinity。

---

## 3. 因子評價（截面策略）

### Rank IC (Spearman)
每天截面計算因子與 forward return 的 Spearman 相關係數。IC 核心指標：
- IC Mean、IC Std、IR = IC Mean / IC Std、Win Rate (IC > 0 比例)

### IC Decay
🚨 **Forward return 欄位僅限離線評估**。`shift(-lag)` 計算的 `fwd_ret_*` **絕不可出現在實盤特徵矩陣中**。

### 分組測試 (Quantile Sort)
🚨 **不可直接跨整個 Panel 計算平均**（會被活躍樣本數多的交易日主導）。正確作法：(1) 先算每日各分組平均收益 (2) 再對時間序列求平均，使每天權重相等。

有效樣本數過低時 `qcut` 會崩潰，需加防護（`try/except ValueError`）。

---

## 4. 交易成本（通用）

必須同時報告 Gross 與 Net Sharpe。成本模型定義詳見 `execution-simulation` skill（固定 bps vs 平方根法則市場衝擊）。

```python
net_returns = gross_returns - turnover * (bps_cost / 10000.0)
```

---

## 5. 換手率分析（截面策略）

### 計算
- 雙邊換手率 = 所有標的權重變動絕對值之和
- 🚨 報告時**必須標明單邊/雙邊**，否則跨策略比較差 2 倍

### 最佳持倉期
不同持倉期下，IC（Gross Sharpe）隨持倉期拉長而衰減，turnover 隨之降低。Net Sharpe 的峰值 = 最佳持倉期。🚨 最佳持倉期會隨 AUM 變化 — AUM 越大，市場衝擊越高，最佳持倉期被迫拉長。

## 6. 容量估算（通用）

任何單一標的的交易量不能超過其日均成交量的某個比例（如 5%）。**最差流動性的標的決定整體容量天花板**，不可用平均值。

---

## 提交前檢查清單

| 類別 | 檢查項目 |
|------|----------|
| **年化一致性** | 年化係數是否統一？有無魔術數字？ |
| **Sharpe ddof** | 專案內 ddof 是否統一？Rf 是否為時間序列？ |
| **Sortino 分母** | 下行標準差分母是否用全樣本長度？ |
| **IC 前視偏誤** | forward return 欄位是否僅用於離線評估？ |
| **分組測試** | 是否先算每日各組平均，再對時間序列求均值？ |
| **交易成本** | 是否同時報告 Gross 與 Net？成本假設是否合理？ |
| **換手率** | 是否標明單邊/雙邊？有無容量估算？ |
