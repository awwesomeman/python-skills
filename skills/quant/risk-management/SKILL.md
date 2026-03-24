---
name: quant-risk-management
description: Portfolio-level risk constraints, exposure controls, VaR/CVaR, leverage, and drawdown-based protections. Use when building risk management systems, defining portfolio constraints, or when the user needs to add risk controls to a strategy.
pipeline_layer: "Risk Layer (Pandas/NumPy)"
---

# 組合風險管理 (Portfolio Risk Management)

> 這是區分「好的回測」和「可以上實盤的回測」的分水嶺。接收 `strategy-construction` 的目標權重，通過風控後送入 `execution-simulation` 做交易模擬。

---

## 1. VaR vs CVaR（通用）

- **VaR**：給定信心水準下的最大損失（分位數）。🚨 VaR 不滿足次可加性 — 兩個組合合併後的 VaR 可能大於各自 VaR 之和
- **CVaR (Expected Shortfall)**：超過 VaR 後的條件期望損失。是一致性風險度量 (Coherent)，滿足次可加性。**Basel III 推薦，實盤優先使用**
- **Parametric VaR**（常態假設）：🚨 金融報酬幾乎都有厚尾與負偏度，常態假設會系統性低估極端風險。僅作快速估算，實盤用 Historical 或 Cornish-Fisher 修正版

---

## 2. 曝險控制（截面策略）

### Gross / Net Exposure
- Gross = |多頭| + |空頭|（總槓桿）。超過 200% 代表槓桿交易
- Net = 多頭 - |空頭|（方向性暴露）。市場中性策略應控制在 ±5%

### 集中度限制
單一標的黑天鵝（財報造假、突發停牌）可能吞噬整個組合的年度收益，必須限制：
- 單一標的最大權重（如 5%）
- 單一行業最大淨權重（如 20%）
- 超標時必須有告警機制

### Factor Exposure
🚨 市場中性策略的 beta 曝險必須控制在 [-0.1, 0.1]，否則策略績效被市場漲跌主導，alpha 被噪音掩蓋。計算方式：`factor_loadings.T @ weights`。

---

## 3. 槓桿（通用）

🚨 槓桿對回撤的影響是**非線性的**：
- 2x 槓桿下，50% 回撤 → 100% 虧損（清算）
- 1.5x 槓桿下，33% 回撤 → 觸發 Margin Call

回測中使用槓桿時，MDD 必須乘以槓桿倍數來評估真實風險。

---

## 4. 回撤保護機制（通用）

### 動態減倉
回撤越深 → 倉位越小。典型階梯：回撤 < 5% 正常操作 → < 10% 減半 → < 15% 減至 25% → > 15% 停止交易 (Kill Switch)。

### Kill Switch
🚨 門檻**不應在回測中最佳化** — 否則你會找到剛好避開所有歷史大跌的門檻 = 過擬合。門檻應基於資金管理紀律預先設定。

典型門檻：日虧 > 5%、週虧 > 8%、月虧 > 12% 任一觸發。

---

## 5. 風險預算（截面策略）

### Risk Parity
目標：使所有資產的風險貢獻 (Risk Contribution = w_i × MRC_i) 相等。

🚨 風險平價只考慮風險分散不考慮收益，低波動資產權重可能 60%+，需搭配槓桿達到目標報酬。

MRC = (Σ @ w) / σ_p，最佳化目標：最小化各資產 Risk Contribution 的方差。

---

## 提交前檢查清單

| 類別 | 檢查項目 |
|------|----------|
| **VaR/CVaR** | 是否優先用 CVaR？常態假設有標記？ |
| **曝險** | Gross/Net 有上下限？逐日監控？ |
| **集中度** | 單一標的與行業權重有限制？ |
| **Factor** | 市場中性 beta 控制在 ±0.1？ |
| **槓桿** | MDD 是否乘以槓桿倍數？ |
| **Kill Switch** | 門檻是否預設（非資料驅動）？ |
