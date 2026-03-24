---
name: quant-coding-standards
description: Coding standards and critical pitfalls specific to quantitative analysis and backtesting. Use when writing, reviewing, or refactoring any quant strategy code. This is the cross-cutting rulebook — all other quant skills assume compliance with this one.
pipeline_layer: "Cross-cutting — 適用於所有 pipeline 層級的通用規範"
---

# 量化開發規範 (Quant Coding Standards)

> 本指南專注於量化開發特有規範。通用 Python 標準（Google Docstring、snake_case 等）詳見 `coding-standards`。Pipeline 流向與 skill 路由詳見 `quant-overview`。

---

## 1. 量化命名慣例（通用）

| 場景 | 規則 |
|------|------|
| 時間欄位 | 專案內統一 `date` 或 `timestamp`，不混用 |
| 資產識別碼 | `asset_id` / `ticker` / `symbol`（選一後統一） |
| 收益率 | `return` / `forward_return` / `ret_fwd_Nd` |
| 函數命名 | 前處理 `prepare_*` / `clean_*`，指標 `calc_*` / `measure_*` |

DataFrame 與 Series 的型別提示必須明確標註（`pd.Series`、`pl.LazyFrame`），因為 Polars 與 Pandas 的 API 行為不同，不標明會在邊界轉換時出錯。

---

## 2. 核心陷阱（通用）

### 2.1 Look-ahead Bias（前視偏誤）

**Panel Data 的 shift/lag 必須隔離資產**：未加 `.over("asset_id")` 就 shift，上一檔的最後一天會洩漏給下一檔的第一天。

```python
# Polars
df.with_columns(pl.col("close").shift(1).over("asset_id").alias("prev_close"))
# Pandas
df.groupby("asset_id")["close"].shift(1)
```

🚨 **Trading Calendar Hazards**：`.shift(1)` 在假日或缺漏時會取錯天。實盤應使用交易日曆對齊（`exchange_calendars`），或用 `join_asof(strategy="backward")`（詳見 `data-preprocessing` §6）。

常見 look-ahead 風險點：rolling、cumsum、merge 後的時序。

### 2.2 IS / OOS 切分必須時序感知

🚨 **絕對禁止** naive random split（如 sklearn 預設的 `train_test_split(df)`）用於時序資料。應使用時序感知的切分方法：純時間切分、Walk-Forward、Purged K-Fold 或 CPCV（詳見 §2.5）。

**有限例外**：純截面模型（如每日獨立的截面迴歸，無時序依賴）若以**日期為單位**做 grouped random split（整天進出、不切割同一天），理論上可接受。但仍建議時序切分以保持方法論一致性。

### 2.3 非重疊取樣

計算 t-stat 時，若前瞻期為 N 天，需每 N 期取一個樣本，避免殘差自相關導致 t-stat 膨脹。推薦用 `scipy.stats.ttest_1samp` 而非手動計算。

### 2.4 小樣本防護

截面資產數或時序期數過短時，統計量不可靠。應回傳 `None` 並記錄 warning，不可靜默產出不可靠數值。

### 2.5 Walk-Forward 與 Purged K-Fold

單次 IS/OOS 切分對 split point 敏感。更穩健的做法：

- **Walk-Forward**：Rolling 或 Anchored expanding window，逐步滑動 train/test。train_window 太短 → 欠擬合；太長 → 包含過時 regime。test_window 必須 ≥ 持倉期。
- **Purged K-Fold (de Prado, 2018)**：從訓練集末端移除 forward return 窗口長度的天數 (purge)，測試集結束後額外排除一段 embargo 天數，防止自相關洩漏。purge_days 必須 ≥ forward return 計算天數。
- **CPCV**：終極版，從 N 個 group 中取 k 個作為測試集的所有組合，全做 purging + embargo，可建構完整 OOS 績效路徑。

---

## 3. 混合架構（Polars + Pandas）（通用）

### 邊界規則
- **Data Pipeline**：建議優先使用 Polars LazyFrame（`pl.scan_parquet()`），效能優勢顯著。Pandas 亦可，關鍵是專案內保持一致
- **ML / Stats**：若使用 Polars，僅在進入 scikit-learn / statsmodels 前才 `.collect().to_pandas()`

### 避免 Pandas 逐行操作
`iterrows()` 和 `apply()` 底層是 Python 迴圈，大數據集上效能極差。效能敏感場景應改用向量化。Prototype 或小數據集上可接受。

### 記憶體與精度
- 高重複字串（`asset_id`）轉 `Categorical` / `Enum`
- 特徵儲存可用 `float32`，但引擎計算（cumprod、矩陣求逆）**硬性要求 `float64`**
- Polars → Pandas → scikit-learn 路徑會觸發 deep copy，超大資料集注意記憶體翻倍

### Pandas MultiIndex 陷阱
量化 Panel Data 常用 `(date, asset_id)` 的 MultiIndex，以下為高頻 bug 來源：
- `groupby` 後 index 可能被 reset 或保留，導致後續 join 失敗 — 養成 `reset_index()` 後再操作的習慣
- `unstack()` / `stack()` 會對缺失的 (date, asset_id) 組合填入 NaN，造成 NaN 擴散 — 需注意 `fill_value` 參數
- `merge` / `join` 時 index 對齊的隱式行為：左右表 index 不一致時靜默產生笛卡爾積或丟失資料 — 建議明確指定 `on` 欄位而非依賴 index 對齊

### Polars 邊界
- rolling 若無時間特徵，只能按 row number 滾動。算交易日 MA 應先 join 交易日曆表
- 事件驅動回測（逐筆更新狀態）應轉向 Numba/Rust，不要強加於 DataFrame

---

## 4. 數值穩定性（通用）

- **浮點比較**：用 `np.isclose()`，絕不用 `== 1.0`
- **矩陣正定性**：Markowitz 前用 `np.linalg.cholesky()` 檢查，非正定則用 shrinkage 或結構化估計器（`strategy-construction` §3）
- **除零保護**：分母加 `EPSILON = 1e-9`，或明確過濾並 log warning
- **ddof 一致性**：Sharpe Ratio 的 `std(ddof=?)` 整個專案必須統一（`performance-evaluation` §2）

```python
EPSILON = 1e-9

# 浮點比較
assert np.isclose(weights.sum(), 1.0), f"Weights sum={weights.sum()}"

# 除零保護
ic = signal_mean / (signal_std + EPSILON)
```

---

## 5. 實驗可重複性（通用）

- 所有隨機操作必須固定 `seed`，集中在 Config 中管理
- 實驗開始時記錄 Python/Pandas/NumPy 版本 — NumPy 跨大版本的 random 產生器行為不同，相同 seed 結果也不同

---

## 提交前檢查清單

| 類別 | 檢查項目 |
|------|----------|
| **Look-ahead** | 時序操作是否先排序？shift/rolling 是否隔離資產？merge 後時序安全？ |
| **IS/OOS** | 切分是否只依時間？有無 random split？ |
| **統計可信度** | 非重疊取樣？小樣本有防護？Walk-forward 或 Purged K-Fold？ |
| **效能** | 大數據集有無 iterrows/apply？Dtype 是否合理？ |
| **數值穩定性** | 浮點比較用 isclose？分母有 epsilon？ddof 統一？ |
| **可重複性** | 固定 seed？參數化頻率？ |
