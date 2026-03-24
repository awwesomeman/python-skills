---
name: quant-execution-simulation
description: Pitfalls for live trading simulation — slippage, liquidity, price limits, short costs, and market impact. Use when building backtesting engines, converting signals to orders, or evaluating execution quality. The goal is to ruthlessly discount your backtest performance toward reality.
pipeline_layer: "Execution Layer (Pandas/NumPy)"
---

# 交易執行模擬 (Execution Simulation)

> 本 skill 不是關於如何產生 Alpha，而是如何**無情地打折你的回測績效**使之貼近實盤。接收 `risk-management` 通過風控的權重，扣除摩擦成本後送入 `performance-evaluation`。

---

## 1. 流動性過濾（截面策略）

「活著」不代表「買得到」。微型股只要下單 10 萬就會造成誇張滑價，模型極易在這些標的上產生虛假的超高 Sharpe。

**必須過濾**：日均成交值 (MDV) 低於門檻的標的，以及絕對股價過低的標的（雞蛋水餃股）。

---

## 2. 漲跌停與零成交（通用，有 price limit 的市場）

在台股、A 股等有漲跌幅限制的市場，漲停鎖死或全天零成交時，**所有買單/賣單皆不應被預設為成交**。

🚨 向量化回測極容易忽略這點 — 在「無法買進的狀態下以漲停價買進」。必須在撮合引擎端檢查 `is_limit_up` / `is_limit_down`，強制失效或遞延至次日。

---

## 3. 下市與破產（通用）

若對報酬率使用無限制 ffill，回測系統會默默幫你「躲過」破產（帳面價格被凍結）。

**必須為下市股票認列強制清算虧損**。破產清算通常歸零 (-100%)，被低價併購可能有回收率，但壓力測試應以 -100% 計。

---

## 4. 執行價格假設（通用）

🚨 **最常見的回測作弊**：在 T 日收盤時計算訊號，並以 T 日 Close 為進場點。這意味著你「看見未來」了。

**正確假設**：T 日收盤計算訊號 → **T+1 日** 以 VWAP 或 Open 執行。

```python
strategy_daily_return = signal_t.shift(1) * vwap_return_t
```

---

## 5. 做空成本（截面策略，Long-Short）

最強的空頭訊號往往指向「券源枯竭 (Hard-to-Borrow)」的標的，融券費率可達年化 20%~100%。回測中預設做空無成本 = 空頭腳 PnL 嚴重虛增。

必須針對空頭部位（負權重）額外扣除每日借券費率。

---

## 6. 市場衝擊與容量（通用）

固定 bps 僅適用小規模。機構實盤中，大部位進出會推動市場價格。

**平方根法則 (Square-Root Law)**：衝擊 ∝ volatility × √(participation_rate)，常數依市場校準（約 0.1）。

🚨 賣單帶負號，直接 `sqrt()` 會產出 NaN 並讓空頭免去滑價成本。必須先 `.abs()` 再開根號。

---

## 7. 結算與企業行為（通用）

- **T+N 交割**：賣出資金不能立刻用於次日買入。Cash Management 需分開記錄「帳面權益」與「可用現金」
- **現金股息**：配息從股價扣除、稍後入帳為現金。回測需明確定義是提取閒置還是 DRIP 再投入。海外投資需扣預扣稅 (Withholding Tax)

---

## 提交前檢查清單

| 類別 | 檢查項目 |
|------|----------|
| **流動性** | 是否過濾 MDV 與低價股？ |
| **漲跌停** | 撮合引擎是否檢查 limit up/down？ |
| **下市** | 下市股票是否認列 -100% 損失？ |
| **執行價格** | 訊號是否 T 日生成、T+1 日執行？ |
| **做空成本** | 空頭部位是否扣除借券費率？ |
| **市場衝擊** | 大規模策略是否使用 impact model 而非固定 bps？ |
| **結算** | 是否考慮 T+N 交割限制？股息處理是否明確？ |
