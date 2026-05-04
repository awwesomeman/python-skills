---
name: jpan-quant
description: Entry point for all quantitative analysis skills. Use whenever the task involves quant strategy development, backtesting, factor research, portfolio construction, or financial data processing. This skill routes to the correct sub-skill based on the task at hand.
pipeline_layer: "Entry Point — 任務路由與 skill 索引"
---

# 量化分析技能索引 (Quant Skills Overview)

> 本 skill 是量化開發的入口。根據當前任務判斷應啟用哪個子 skill。

---

## Pipeline 流向

```
data-preprocessing → strategy-construction → risk-management → execution-simulation → performance-evaluation
   (Polars)              (混合)                (Pandas/NumPy)     (Pandas/NumPy)       (Pandas/NumPy/SciPy)
                                                                                              │
                                                                                    ┌─────────┴──────────┐
                                                                               regime-analysis    multiple-testing
```

> `coding-standards` 是所有子 skill 的前置依賴，任何量化任務都必須同時載入。

> 標記為 `(截面策略)` 的章節僅適用於多資產截面選股。其他策略類型可跳過這些章節。

## 任務路由

判斷任務類型後，以**本檔案所在目錄**為基準，**直接讀取**對應子目錄的 SKILL.md 並依照規範執行，不需要詢問使用者確認。若父層與子層規則衝突，以子層為準。

| 任務 | 載入的 Skill（相對於本目錄） |
|------|------|
| 資料清洗 / 特徵工程 | [data-preprocessing/SKILL.md](./data-preprocessing/SKILL.md) |
| 因子研究（IC、分組測試） | [data-preprocessing/SKILL.md](./data-preprocessing/SKILL.md) + [performance-evaluation/SKILL.md](./performance-evaluation/SKILL.md) + [multiple-testing/SKILL.md](./multiple-testing/SKILL.md) |
| 截面選股策略開發 | 全部（沿 pipeline 流向） |
| 其他策略類型（單資產 / CTA / 配對交易等） | 全部（沿 pipeline 流向，跳過截面策略章節） |
| 策略穩健性檢驗 | [performance-evaluation/SKILL.md](./performance-evaluation/SKILL.md) + [regime-analysis/SKILL.md](./regime-analysis/SKILL.md) + [multiple-testing/SKILL.md](./multiple-testing/SKILL.md) |

## Skill 簡表

| Skill | 定位 |
|-------|------|
| **coding-standards** | 跨層通用規範：前視偏誤、數值穩定性、Polars/Pandas 架構 |
| **data-preprocessing** | 資料清洗、缺失值、去極值、標準化、跨頻率對齊 |
| **strategy-construction** | §1 通用策略設計原則 + §2-6 截面選股的信號組合與權重分配 |
| **risk-management** | VaR/CVaR、曝險控制、槓桿、回撤保護、風險預算 |
| **execution-simulation** | 滑價、漲跌停、市場衝擊、做空成本、結算 |
| **performance-evaluation** | Sharpe/MDD/Sortino 陷阱、因子評價、換手率分析 |
| **multiple-testing** | FDR 校正、Haircut Sharpe、Placebo Test、實驗日誌 |
| **regime-analysis** | Regime 分類、結構性斷裂偵測、循環論證防護 |