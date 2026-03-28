---
name: coding-standards
description: Python 編碼標準（命名、錯誤處理、async、typing、測試）。撰寫、審查、重構 Python 程式碼時使用。
---

# Python 編碼標準

編寫 Python 程式碼時，遵循以下標準。各規則的 ❌/✅ 對照寫法見 `examples/` 目錄。

## 核心原則

| 原則 | 說明 |
|------|------|
| **可讀性優先** | 清晰的命名、自我說明的程式碼 |
| **KISS** | 最簡單有效的解決方案，避免過度設計 |
| **DRY** | 抽取共用邏輯，避免複製貼上 |
| **YAGNI** | 不預先建立不需要的功能 |

## Decision Tree：選擇正確的模式

```
編寫程式碼 → 是什麼類型？
    ├─ 函式/方法 → 參考：命名規範、錯誤處理
    ├─ API 端點 → 參考：examples/api_design.py、錯誤處理
    ├─ 非同步操作 → 參考：非同步並行、examples/async_patterns.py
    ├─ 資料模型 → 參考：型別標註、examples/type_annotations.py
    └─ 測試程式 → 參考：最佳實踐 §測試、examples/testing_patterns.py
```

## 快速參考

### 命名規範

| 類型 | 風格 | 範例 |
|------|------|------|
| 變數 / 函式 | `snake_case` | `market_search_query`, `fetch_market_data()` |
| 類別 | `PascalCase` | `MarketService` |
| 常數 | `SCREAMING_SNAKE_CASE` | `MAX_RETRIES = 3` |
| 模組 / 套件 | `snake_case` | `market_service.py`, `utils/` |
| 私有成員 | `_snake_case` | `_internal_cache`, `_parse_row()` |
| Type Alias | `PascalCase` | `UserId = str` |

函式命名使用**動詞-名詞**模式：`fetch_user`、`calculate_score`、`validate_input`。
完整範例見 `examples/naming_conventions.py`。

### 錯誤處理

- 捕獲**特定例外**，不要 bare `except`；用 `from e` 保留原始 traceback
- logging 格式化與日誌等級規範詳見 `logging` skill
- 詳見 `examples/error_handling.py`

### 非同步並行

- 可並行的獨立操作使用 `asyncio.gather()`，不要循序 await，因為循序執行會讓總耗時等於各操作耗時之和
- 詳見 `examples/async_patterns.py`

### 型別標註

- 所有函式參數和回傳值都要標註型別，不使用 `Any`
- 資料模型優先使用 `dataclass` 或 `Pydantic`，搭配 `Literal` 限縮值域
- 詳見 `examples/type_annotations.py`

## Import 排序

依序分組：① 標準函式庫 ② 第三方套件 ③ 本地模組，各組空一行。使用 `ruff` 的 `isort` 規則自動排序。

## Docstring 與註解

- 統一使用 **Google style** docstring；簡單函式可只寫一行摘要，多參數時使用 `Args / Returns / Raises` 完整格式
- 每個模組開頭加**架構定位說明**（輸入層/輸出層），幫助 AI 快速建立上下文
- 非直觀的設計加 `# WHY:` 註解，解釋**動機**而非行為，因為行為看程式碼就知道，但動機只存在於作者腦中

## 專案結構

- **單一職責 (SRP)**：每個函式只做一件事，由呼叫端組合多步驟流程
- **依賴注入**：相依物件透過參數傳入，不在函式內硬編碼實例，因為硬編碼無法在測試中替換為 mock
- **入口保護**：可執行腳本加 `if __name__ == "__main__": main()`
- ❌/✅ 對照見 `examples/over_engineering.py`

## 避免過度開發

```
這段程式碼是否解決了當前的問題？
    ├─ 是 → 停下來，不要繼續「改善」
    └─ 否 → 用最簡單的方式解決它
```

### 何時該抽象？

| 條件 | 行動 |
|------|------|
| 邏輯只出現 1 次 | 不要抽象，保持 inline |
| 邏輯出現 2 次 | 考慮是否真的相同，通常先容忍重複 |
| 邏輯出現 3 次以上 | 抽取為函式或類別（Rule of Three） |
| 有明確的多型需求 | 使用 Protocol 或 ABC |
| 只是「覺得以後可能需要」 | **不要做** |

> 反模式範例（過早抽象、預測未來需求、過度防禦、過度包裝）見 `examples/over_engineering.py`。

## 常見陷阱

| 陷阱 | 正確做法 | 原因 |
|------|----------|------|
| 使用 `Any` 或省略型別 | 明確標註所有參數和回傳值 | 破壞靜態檢查，runtime error 難追蹤 |
| 使用魔術數字 | 定義有意義的常數名稱 | 失去語意，後續修改容易漏改 |
| 巢狀超過 3 層 | 使用 early return 減少巢狀 | 大幅增加認知負荷與圈複雜度 |
| `datetime.now()` | `datetime.now(timezone.utc)` | naive datetime 無時區，跨系統比對會出錯 |

## 最佳實踐

- **測試**：使用 AAA 模式（Arrange-Act-Assert），詳見 `examples/testing_patterns.py`
- **效能**：`@lru_cache` 快取昂貴計算，生成器處理大型資料
- **資源**：使用 `with` 語句管理資源（檔案、連線）

## 工具鏈

| 工具 | 用途 | 指令 |
|------|------|------|
| `ruff` | Linting + import 排序 + 格式化 | `ruff check --fix && ruff format` |
| `mypy` | 靜態型別檢查 | `mypy --strict` |
| `pytest` | 測試 | `pytest -v` |

建議在 CI 和 pre-commit hook 中整合以上工具。

## 提交前檢查清單

| 檢查項目 |
|----------|
| 所有函式參數和回傳值都有型別標註？ |
| 沒有使用魔術數字？常數有命名？ |
| 巢狀沒有超過 3 層？用了 early return？ |
| `datetime` 使用 `timezone.utc`？ |
| Import 依照 標準庫 → 第三方 → 本地 排序？ |
| 非直觀設計有 `# WHY:` 註解？ |
| 沒有過度抽象（Rule of Three）？ |

## 範例檔案

| 檔案 | 內容 |
|------|------|
| `examples/naming_conventions.py` | 命名規範、變數/函式/類別範例 |
| `examples/error_handling.py` | 錯誤處理、logging 模式 |
| `examples/async_patterns.py` | 非同步並行模式 |
| `examples/type_annotations.py` | 型別標註與資料模型 |
| `examples/testing_patterns.py` | pytest 測試模式與 fixtures |
| `examples/api_design.py` | FastAPI 端點設計模式 |
| `examples/over_engineering.py` | 過度開發反模式、SRP/DI 對照 |
