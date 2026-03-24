---
name: quant-strategy-construction
description: Universal strategy design principles (§1) plus detailed cross-sectional signal combination and weight allocation (§2-6). Use when designing any quant strategy, or specifically when building portfolios from factor signals.
pipeline_layer: "Strategy Layer (混合 Polars/Pandas/NumPy)"
---

# 策略構建 (Strategy Construction)

> §1 為所有策略類型通用的設計原則。§2-6 專注於截面選股的信號組合與權重分配。

---

## 1. 通用策略設計原則（通用）

### 過擬合防護
IS 表現優於 OOS 是常態而非例外。參數越多、回測期越短，衰減越嚴重。經驗法則：自由參數數量應 < 樣本年數的 2 倍。策略邏輯應有明確的經濟學直覺支撐，純統計挖掘的策略衰減最快。

### 信號半衰期
所有信號都有衰減曲線（decay profile）。持倉期應匹配信號半衰期 — 持倉太短白付交易成本，太長信號已失效仍在持有。需在不同持倉期下比較 Net Sharpe 找最佳平衡點（詳見 `performance-evaluation` §5）。

### 交易成本敏感度
Gross Sharpe → Net Sharpe 的落差是策略可行性的核心指標。Gross 2.0 但 Net 0.3 的策略不值得上線。開發初期就應估算成本影響（詳見 `execution-simulation`）。

### Regime 依賴性
任何策略都隱含對市場環境的假設。動能策略在趨勢市賺錢、震盪市虧錢；均值回歸反之。必須在開發階段就理解策略的 regime 依賴（詳見 `regime-analysis`），而非上線後被打臉才分析。

### 容量天花板
策略容量受最差流動性標的限制。AUM 越大，市場衝擊越高，最佳持倉期被迫拉長，Net Sharpe 下降。開發初期就應估算容量上限，避免花大量時間開發無法承載目標 AUM 的策略。

---

## 2. 信號組合（截面策略）

### 組合前必須標準化
🚨 各因子必須已經過截面標準化（z-score 或 rank），否則量綱不同的因子被數值大的主導。

### 組合方法
- **等權**：最簡單最穩健的 baseline，直接 `signals.mean(axis=1)`
- **IC 加權**：依歷史 IC 均值分配權重。🚨 IC 必須用 rolling 歷史值（非全段），否則前視偏誤。IC < 0 的因子權重應設為 0
- **最大化 IR**：理論最優但對估計誤差極敏感，實盤中等權往往更穩健

### 因子相關性
🚨 高度相關的因子（如不同 lookback 的動能）在等權組合中隱性 over-weight 同一主題。建議 corr > 0.7 的群組只保留 IC 最高的一個，或先 PCA 降維。

### Signal Decay
信號更新頻率低於再平衡頻率時（如週頻信號 + 日頻交易），對信號施加指數衰減（EWM with half-life）。

---

## 3. 權重分配（截面策略）

### 等權 Long-Short
做多信號最強的 top quantile，做空最弱的 bottom quantile，各內部等權。最不依賴假設的方法。

### 信號比例加權
權重 ∝ 信號強度，縮放至目標 Gross Exposure。🚨 信號必須已去極值，否則極端 z-score 的個股集中過多資金。去均值確保 long/short 對稱。

### Mean-Variance 最佳化
🚨 三大陷阱：
1. 樣本共變異數矩陣在 N > T 時極不穩定 — **必須用 Ledoit-Wolf shrinkage**
2. 對預期收益 μ 極度敏感 — 微小變動 → 權重劇烈翻轉。實盤建議 Black-Litterman 或直接 minimum variance（不依賴 μ）
3. 資產數 > 200 時 solver 可能慢或收斂到局部解

---

## 4. 再平衡（通用）

### 日曆式 vs 門檻式
- **日曆式**（月末/週末觸發）：劇烈行情中反應太慢
- **門檻式**（偏離 > threshold 觸發）：震盪市中頻繁交易
- **實盤建議**：組合使用 — 到期或超標，任一觸發

### Buffer Zone
只調整偏離超過 buffer 的標的，其餘保持不動。可顯著降低換手率。

🚨 歸一化後用 `np.isclose()` 檢查（不可 `!= 0`），遵循 coding-standards 的浮點比較規範。

---

## 5. 組合約束（截面策略）

🚨 **回測中就要施加所有實盤約束**，而非事後調整。「最佳化權重」和「可執行權重」的差距是回測 vs 實盤績效落差的主因。

施加順序：
1. Long-only 約束（若適用）→ clip(lower=0)
2. 單一標的限制 → clip(-max, max)
3. 行業限制 → 超標行業等比例縮放
4. Gross Exposure 限制 → 全部等比例縮放

---

## 6. 端對端流程（截面策略）

```
原始因子 → 截面標準化 → 信號組合（等權/IC-weighted）→ 信號比例加權 → 施加約束 → 目標權重
```

🚨 從信號到權重的完整路徑必須在同一時間截面內完成（無跨期洩漏）。IC 權重需用 expanding/rolling 歷史值。權重送入 risk-management skill 做曝險檢查。

---

## 提交前檢查清單

| 類別 | 檢查項目 |
|------|----------|
| **過擬合** | 策略邏輯有經濟學直覺？參數數量合理？IS/OOS 衰減可接受？ |
| **成本可行性** | Gross → Net Sharpe 落差是否在可接受範圍？ |
| **信號標準化** | 組合前各因子是否截面標準化？量綱一致？ |
| **因子相關性** | corr > 0.7 的冗餘因子是否處理？ |
| **IC 權重** | IC 是否用 rolling 歷史值（非全段）？ |
| **權重約束** | 回測是否已施加所有實盤約束？ |
| **再平衡** | 頻率與持倉期匹配？有 buffer zone？ |
| **最佳化** | 共變異數是否 shrinkage？資產數合理？ |
| **端對端** | 信號到權重在同一截面完成？無跨期洩漏？ |
