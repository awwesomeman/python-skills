---
name: quant-multiple-testing
description: Standards for controlling false discovery when evaluating multiple strategies or factors. Use when running factor screening, strategy selection, parameter sweeps, or any batch hypothesis testing in quant research. Also use when the user has tested multiple variations and is selecting the "best" one.
pipeline_layer: "Stats Layer (NumPy/SciPy)"
---

# 多重檢定與統計紀律 (Multiple Testing)

> 測試 100 個因子，5% 顯著水準下期望 5 個假陽性 — 這不是風險，是**必然**。不控制多重檢定，你的研究成果就是在挑選噪音。接收 `performance-evaluation` 的因子統計量進行校正。

---

## 1. 隱形多重檢定（通用）

以下行為**都等同於多重檢定**，即使沒有明確跑假設檢定：

| 行為 | 等效 K |
|------|--------|
| 測試 50 個技術指標找最好的 3 個 | 50 |
| 對同一因子嘗試 10 種參數組合 | 10 |
| 在 3 個不同 universe 上回測同一策略 | 3 |
| 5 種持倉期 × 4 種加權方式 | 20 |
| 團隊 A 測 30 個 + 團隊 B 測 40 個，合併選最好 | 70 |

🚨 K 必須計入**所有曾經嘗試過的變體**，包括被丟棄的「失敗實驗」。僅報告倖存者的 t-stat 就是在作弊。

---

## 2. 校正方法選擇（通用）

| 方法 | 控制目標 | 何時用 |
|------|---------|--------|
| **Bonferroni** | FWER（任何假陽性 ≤ α） | 因子 < 20、需最嚴格控制 |
| **Holm-Bonferroni** | FWER（逐步放寬） | 比 Bonferroni 略寬鬆 |
| **BH-FDR**（實戰首選） | FDR（假陽性比例 ≤ q） | 因子數量多、容忍少量假陽性 |
| **BY-FDR** | FDR（任意相關結構） | 因子高度相關（如不同 lookback 動能）|

🚨 BH 假設各檢定獨立或正相關 (PRDS)。量化因子通常高度相關，此時應用 BY 校正（額外除以調和級數 $\sum 1/i$）。

---

## 3. Haircut Sharpe Ratio（通用）

無法精確列舉所有測試次數時（如跨團隊累積歷史），直接對 Sharpe 打折。

核心邏輯：觀察到的 Sharpe 轉為 t-stat → 減去多重檢定下的期望最大值 `E[max(Z_1,...,Z_K)]` → 轉回 Sharpe。

| 校正後 Sharpe | 判讀（中高頻截面策略） |
|--------------|------|
| > 2.0 | 極強，仍需確認非資料錯誤 |
| 1.0 ~ 2.0 | 有潛力，值得 OOS 驗證 |
| 0.5 ~ 1.0 | 邊緣，可能需組合其他因子 |
| < 0.5 | 大機率為噪音 |

> 上表適用於中高頻截面策略。低頻配置型策略（月頻再平衡、高容量）的可接受門檻更低，Net Sharpe 0.3~0.5 在機構配置中仍屬合理。

🚨 Harvey et al. (2016) 建議：新因子的 t-stat 應至少 **3.0**（非傳統 1.96）才算顯著。此門檻主要針對無法精確追蹤總測試次數 K 的場景（如引用外部學術研究、跨團隊累積歷史）。若已做 FDR 校正且 K 精確已知，可沿用校正後的顯著性水準，不必額外要求 t > 3.0（避免雙重懲罰）。

---

## 4. Placebo Test（通用）

在宣稱因子有效前，將因子值在截面內隨機打亂（permutation），計算虛假 IC 的分佈。真實 IC 必須顯著優於此隨機基準線（經驗 p-value < 0.05）。

核心：逐截面 `rng.permutation(factor_values)` → 計算 shuffled Spearman IC → 重複 1000 次建構 null distribution。

---

## 5. Deflated Sharpe Ratio（進階）

DSR (Bailey & López de Prado, 2014) 額外考慮報酬的偏度與峰度，估算觀察到的 SR 為「真正顯著」的機率。SR 估計量的標準誤公式含偏度/峰度修正項：`sqrt((1 - skew×SR + (kurt_excess/4)×SR²) / (n-1))`。

適用於報酬分佈有顯著負偏或厚尾的策略（如賣選擇權）。

---

## 6. 實驗日誌（通用）

多重檢定校正的前提是**知道自己測了多少次**。沒有日誌，一切校正都是空談。

- 所有實驗（含失敗、放棄的）都必須記錄 — 因子名、參數、universe、日期範圍、IC、Sharpe、t-stat
- 🚨 絕對禁止只記錄「成功」的實驗 — 等同於事後篡改 K 值
- 定期對所有已完成實驗做 BH-FDR 回顧，檢查被選中的因子是否通過校正

---

## 提交前檢查清單

| 類別 | 檢查項目 |
|------|----------|
| **實驗記錄** | 所有測試（含失敗）是否都已記錄？K 反映真實嘗試次數？ |
| **FDR 校正** | 宣稱顯著的因子是否通過 BH-FDR（或 BY）？ |
| **Haircut SR** | Sharpe 是否經過多重檢定折扣？折扣後 > 0.5？ |
| **Placebo** | 真實 IC 是否顯著優於隨機基準線？ |
| **t-stat 門檻** | K 未精確追蹤時 t-stat ≥ 3.0？已做 FDR 校正時沿用校正後顯著性水準？ |
| **隱形多重檢定** | 參數掃描、universe 切換、持倉期變體是否計入 K？ |
