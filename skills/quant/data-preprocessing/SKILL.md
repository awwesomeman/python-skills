---
name: quant-data-preprocessing
description: Pitfalls and standards for cleaning, transforming, and standardizing quantitative financial data in the context of quant strategy backtesting. Use when working on feature engineering, data pipelines, or any data cleaning for quant strategies.
pipeline_layer: "Data Layer (Polars LazyFrame)"
---

# 量化資料前處理規範 (Data Preprocessing)

> 建議優先使用 Polars Lazy API（邊界規則詳見 `coding-standards` §3）。可獨立用於資料清洗，也可作為策略開發 pipeline 的第一步。

---

## 1. 報酬率計算（通用）

| 場景 | 應使用 | 原因 |
|------|--------|------|
| 多資產組合報酬（截面加權） | **Simple Return** `P_t/P_{t-1} - 1` | 組合報酬 = Σ(w_i × r_i)，log return 不滿足線性可加性 |
| 多期累積報酬（時間聚合） | **Log Return** `ln(P_t/P_{t-1})` | 直接 `.sum()` 即可 |
| 統計模型（OLS、因子分析） | **Log Return** | 更接近常態分佈假設 |
| 回測績效報告、Sharpe 計算 | **Simple Return** | 業界慣例 |

🚨 **絕對禁止**對 simple return 用 `.sum()` 算累積報酬。連跌 -10% 兩天，sum = -20% 但實際 = -19%。必須用 `(1 + r).cumprod() - 1`。

---

## 2. 缺失值處理（通用）

### 回測 Pipeline 中禁止 Backward Fill
在回測或特徵建構 pipeline 中，對**時間序列方向**用未來的資料填補過去 = 前視偏誤。EDA、target variable 建構（如 forward return）、或非回測的資料清洗場景不在此限。

**例外**：以下情況的 backward fill 不構成前視偏誤：
- **已知靜態映射表**：如行業分類碼的生效日 backward fill 到該期間內所有日期（資訊在生效日即已公開）
- **同一時間截面內**：如盤中逐筆行情的缺漏補回（不涉及跨期）

```python
# ❌ 用明天的價格填今天
df.with_columns(pl.col("price").fill_null(strategy="backward"))
# ❌ 用全段均值填（時間序列方向上包含未來資料）
df.with_columns(pl.col("pe_ratio").fill_null(pl.col("pe_ratio").mean()))
```

### Forward Fill 必須加 limit
慢速變數（如財報）的 ffill 不設上限，會讓過期資料無限展期。必須設合理天數限制，且先確保時間排序。limit 應依市場法定公佈時限設定（如台股季報法定 45 天，可用 `limit=60~65`；美股 10-Q 法定 40~45 天，可用 `limit=55~60`）。對變化快速的基本面因子宜更保守。

### Polars NaN ≠ null 陷阱
🚨 Polars 的 `.fill_null()` **不會處理浮點數 NaN**。從 Pandas 轉入的資料常混有 NaN，必須先 `.fill_nan(None)` 再做任何填補：

```python
cs.numeric().fill_nan(None).forward_fill(limit=65).over("asset_id")
```

---

## 3. 去極值（截面策略）

優先使用 **MAD (Median Absolute Deviation)** 而非標準差，因為標準差本身受極端值影響。

核心邏輯：`median ± n_mad × MAD × 1.4826`（1.4826 為常態一致性常數），用 `.clip()` 截斷。`n_mad` 常見取值：**3**（等效常態 3σ，適合 ML 特徵，較積極截斷）、**5**（等效常態 5σ，適合截面選股，保留更多尾部資訊）。預設建議 **5**，除非有明確理由需要更積極的截斷。

🚨 **Expression Context 陷阱**：在 Polars 中，`median()` 的計算範圍取決於 `.over()` 的 partition。必須搭配 `.over("date")` 確保在每個時間截面內獨立計算，否則 median 會對整欄求值（跨期混合 = 前視偏誤）。

**進階替代**：MAD clip 會在分佈兩端產生斷層 (mass points)，對梯度更新的 ML 模型可能有害。可考慮 Tanh squashing 做平滑擠壓。

---

## 4. 標準化（截面策略）

排名、Z-score、分組等截面操作必須**限定在同一時間截面**。

### Z-Score
`(x - mean) / std`，必須搭配 `.over("date")`。

### Percentile Rank
建議用 `rank / count()` 而非 `rank / rank.max()`，因為有同分 (ties) 時 `max()` 會把同分群壓縮到 100%。

### Gaussian Rank（送入 ML 前）
排名需減 0.5 再除以 count，防止最高/最低分觸發 `ppf(1.0) = Infinity`：
```python
(pl.col("signal").rank(method="average") - 0.5) / pl.col("signal").count()  # 必須搭配 .over("date")
```

🚨 **絕對禁止**對整個 DataFrame 直接 `rank()` 不加 `.over("date")` — 會混合所有日期。

---

## 5. 截面中性化（截面策略）

用 OLS 迴歸取殘差消除行業/市值風格影響。此步屬於 Stats Layer，允許用 Pandas。

關鍵陷阱：
- **缺失值處理**：直接 `dropna` 會大量流失樣本。應先做行業中位數插補 (Industry Median Imputation)。
- **共線性**：行業虛擬變數 + 市值容易共線。實盤建議改用 Ridge 或預先 PCA。
- **市值取對數**：原始市值極度右偏，必須 `np.log(market_cap)` 後再進迴歸（市值恆正，不需要 `+1`）。

---

## 6. 跨頻率對齊（通用）

### 黃金標準：`join_asof` + `strategy="backward"`
對齊不同頻率（如日頻股價 + 季度財報）時，優先使用 `join_asof`，語義更明確且不易出錯。若用 `left_join` + `ffill`，必須確認 ffill 不會把未來資料填入：

```python
df_daily.join_asof(df_quarterly,
    left_on="date", right_on="publish_date",  # 🚨 用發佈日，不是報表截止日
    by="asset_id", strategy="backward")
```

### 高頻轉低頻
必須區分存量指標（取 `.last()`，如收盤價）和流量指標（取 `.sum()`，如成交量）。注意 `group_by_dynamic` 的 `closed` 參數。

---

## 7. 存活者偏差與 Point-in-Time（通用）

### 回測宇宙必須動態
回測宇宙必須使用**回測當時的歷史成分股**，不可用現在的指數成分回測過去。已下市、被剔除的公司必須存在於歷史宇宙中，否則回測結果虛高。

### Point-in-Time 資料
財報必須用**發佈日 (publish_date)**，不可用報表截止日 (report_date)。宏觀數據（GDP、PMI）必須使用初值序列，不可用修訂版。

### 復權價格
- **特徵計算**：使用全復權價格 (Adjusted Close)
- **交易模擬**：使用未復權真實價格 (Raw Close)，因為滑價和最小交易單位受絕對股價限制

---

## 提交前檢查清單

| 類別 | 檢查項目 |
|------|----------|
| **報酬率** | simple vs log return 是否用對場景？累積報酬是否用 cumprod？ |
| **缺失值** | 有無 backward fill？ffill 是否有 limit？NaN 是否先轉 null？ |
| **截面隔離** | 所有截面操作（rank、z-score、去極值）是否都有 `.over("date")`？ |
| **頻率對齊** | 跨頻率合併是否用 `join_asof`？右表是否使用 publish_date？ |
| **存活者偏差** | 回測宇宙是否動態？是否包含已下市標的？ |
| **復權** | 特徵計算用 adjusted close、交易模擬用 raw close？ |
