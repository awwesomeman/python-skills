---
name: quant-regime-analysis
description: Standards for regime-conditional performance decomposition and structural break detection. Use when evaluating strategy robustness across different market environments, or when strategy performance suddenly degrades.
pipeline_layer: "Stats Layer (Pandas/NumPy/SciPy)"
---

# Regime 分析與結構性斷裂 (Regime Analysis)

> 策略在牛市賺錢不代表能活過熊市。不做 regime 拆解 = 把晴天傘當防暴雨傘。接收 `performance-evaluation` 的報酬序列進行 regime 拆解。

---

## 1. Regime 分類方法（通用）

### 規則式（無前視風險）
- **波動率分位**：用 realized volatility 的 expanding 分位數切分低/中/高。🚨 必須用 expanding window（只看歷史），不可用全段分位數。
- **Bull/Bear/Sideways**：用滾動累積收益判定。lookback、threshold 都是超參數，需預先設定。

### 數據驅動式（有前視風險）
- **HMM (Hidden Markov Model)**：可自動發現隱藏狀態，但 🚨 必須在 IS 期間訓練、OOS 期間推論。**絕對禁止**在全段 fit 後回標歷史 regime。
- HMM 對初始值敏感，建議多次 random restart 取最高 log-likelihood。
- 狀態編號無固有意義（每次 fit 可能 0/1 對調），**必須依 mean return 重新排序**。

---

## 2. Regime-Conditional 績效拆解（通用）

分 regime 計算 Sharpe、MDD、Win Rate 等指標。

🚨 **樣本數要求**：每個 regime 至少 60 個交易日，否則統計量不可靠，必須標記。

### 轉移矩陣
計算 regime 間的轉移機率，觀察切換頻率。同時檢查 regime 切換後 N 天的策略 PnL — 若策略在 regime 轉換時系統性虧損，說明它對 regime shift 脆弱。

### 🚨 最重要的警告：循環論證
將 HMM 在全段 fit，然後用 regime 標籤評估策略的「分 regime 表現」= **循環論證**。模型會自動把好/壞績效歸因到不同 regime，讓每個 regime 內的 Sharpe 都比整體高。

正確做法：規則式分類（不含未來）或 walk-forward refit HMM。

---

## 3. 結構性斷裂偵測（通用）

### CUSUM（Page's Cumulative Sum）
偵測均值漂移。遞迴公式 `S_t = max(0, S_{t-1} + x_t)`，超過 threshold 即警告。

🚨 不可用 `cumsum().clip(lower=0)` 近似 — 該寫法不會在歸零後重置，會系統性低估偏移。

### Rolling Stability
最實用的日常監控：rolling Sharpe、rolling IC。🚨 窗口至少 126 個交易日（半年），太短波動極大易誤判。

### Chow Test
在候選斷點處分段 OLS，檢驗係數是否顯著不同。適用於確認「Sharpe 顯著下降」是否為結構性變化。

---

## 提交前檢查清單

| 類別 | 檢查項目 |
|------|----------|
| **前視偏誤** | 波動率門檻是否用 expanding（非全段）？ |
| **HMM** | 是否 IS 訓練 / OOS 推論？狀態是否依 mean return 排序？ |
| **樣本數** | 每 regime ≥ 60 天？不足是否標記？ |
| **循環論證** | regime 標籤生成是否獨立於策略績效？ |
| **Rolling** | 窗口 ≥ 126 天？ |
