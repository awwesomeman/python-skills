---
name: coding-standards
description: Defines Python coding standards (naming, error handling, async, typing, testing). Use when writing, reviewing, or refactoring Python code.
---

# Python 編碼標準

編寫 Python 程式碼時，遵循以下標準確保程式碼品質與一致性。

**範例檔案可用**：
- `examples/` - 包含各種模式的詳細程式碼範例

**需要時參考範例** - 先理解核心原則，需要具體實作時再查看 examples/ 目錄中的範例檔案。

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
    │
    ├─ API 端點 → 參考：API 設計、輸入驗證、錯誤處理
    │
    ├─ 非同步操作 → 參考：非同步模式（asyncio.gather）
    │
    ├─ 資料模型 → 參考：型別標註、dataclass/Pydantic
    │
    └─ 測試程式 → 參考：測試標準（AAA 模式、pytest）
```

## 快速參考

### 命名規範
```python
# 變數/函式：snake_case
market_search_query = 'election'
def fetch_market_data(market_id: str) -> dict: ...

# 類別：PascalCase
class MarketService: ...

# 常數：SCREAMING_SNAKE_CASE
MAX_RETRIES = 3
```

### 錯誤處理
```python
try:
    result = await risky_operation()
except SpecificError as e:
    logger.error('操作失敗: %s', e)  # 使用 % 格式化
    raise ValueError('操作失敗') from e
```

**日誌等級運用**：
- `logger.debug()`: 處理細節、變數狀態
- `logger.info()`: 重要流程節點完成（如初始化、批次處理完畢）
- `logger.warning()`: 非致命異常（如退回使用預設值、重試中）
- `logger.error()`: 導致服務中斷需修復的具體錯誤

### 非同步並行
```python
# ✅ 可並行時使用 gather
users, markets = await asyncio.gather(
    fetch_users(),
    fetch_markets()
)
```

### 型別標註
```python
from dataclasses import dataclass
from typing import Literal

@dataclass
class Market:
    id: str
    status: Literal['active', 'resolved', 'closed']
```

## Import 排序

依照以下順序分組，各組之間空一行：

```python
# 1. 標準函式庫
import asyncio
import logging
from datetime import datetime, timezone

# 2. 第三方套件
import httpx
from fastapi import APIRouter
from pydantic import BaseModel

# 3. 本地模組
from myapp.models import User
from myapp.services import UserService
```

> 使用 `ruff` 的 `isort` 規則可自動排序。

## Docstring 風格

統一使用 Google style docstring：

```python
def fetch_data(url: str, timeout: float = 30.0) -> dict[str, Any]:
    """取得遠端資料。

    Args:
        url: 目標 URL
        timeout: 超時秒數

    Returns:
        解析後的 JSON 資料

    Raises:
        ValueError: 當請求失敗時
    """
```

- 簡單函式可只寫一行摘要
- 有多個參數、回傳值或可能拋出例外時，使用完整格式

### 模組級說明（AI 上下文錨點）

每個檔案開頭用簡短說明描述其在架構中的定位，幫助 AI 快速建立上下文：

```python
"""
myapp/services/user_service.py

處理使用者相關的業務邏輯（註冊、登入）。
輸入層：API Router；輸出層：User Repository。
"""
```

### `# WHY` 註解

代碼中每個非直觀的設計都需解釋**動機**，而非**行為**：

```python
# ❌ WHAT（說了等於沒說）
# 將超時設為 5 秒
timeout = 5.0

# ✅ WHY（解釋選擇的理由）
# WHY: 上游 API 在高負載時的 P99 響應時間約為 4.5 秒，設為 5 秒能避免提早中斷
timeout = 5.0
```

## 專案結構與模組化

### 單一職責原則 (SRP)

每個模組或函式只做一件事：

```python
# ❌ 一個函式同時做了資料獲取、計算、寫出檔案
def process_data():
    data = fetch_api()
    result = compute(data)
    save_to_db(result)

# ✅ 各自分離，便於測試與重用
def fetch_and_process():
    data = fetch_api()
    return compute(data)
```

### 依賴注入（提升可測性）

透過函式參數傳入依賴，不在函式內部硬編碼實例：

```python
# ✅ 推薦：相依物件透過參數傳入，可被測試替換 (Mock)
def process_order(order: dict, db_client: DatabaseClient) -> bool:
    ...

# ❌ 避免：在函式內讀取 global 狀態，難以隔離測試
def process_order(order: dict) -> bool:
    db_client = get_global_db_client()
    ...
```

### 入口保護

為可執行的腳本提供入口保護，避免被 import 時意外執行：

```python
if __name__ == "__main__":
    main()
```

## 避免過度開發

過度開發（Over-engineering）是指在當前需求尚不需要的情況下，預先設計過於複雜的架構或抽象層。Python 哲學強調「Simple is better than complex」。

### 判斷原則

```
這段程式碼是否解決了當前的問題？
    ├─ 是 → 停下來，不要繼續「改善」
    └─ 否 → 用最簡單的方式解決它
```

### 常見的過度開發模式

**1. 過早抽象：只用一次的東西不需要包裝**

```python
# ❌ 只有一個實作卻建立了抽象層
class DataSourceBase(ABC):
    @abstractmethod
    def fetch(self) -> list[dict]: ...

class PostgresDataSource(DataSourceBase):
    def fetch(self) -> list[dict]:
        return self.db.query("SELECT * FROM users")

# ✅ 直接寫，等到真正有第二個實作時再抽象
class UserRepository:
    def fetch_users(self) -> list[dict]:
        return self.db.query("SELECT * FROM users")
```

**2. 不必要的設計模式：三行能解決的事不需要一個 class**

```python
# ❌ 為了「可擴展性」寫了策略模式
class ValidationStrategy(Protocol):
    def validate(self, value: str) -> bool: ...

class EmailValidator:
    def validate(self, value: str) -> bool:
        return "@" in value

class ValidatorEngine:
    def __init__(self, strategy: ValidationStrategy) -> None:
        self._strategy = strategy

    def run(self, value: str) -> bool:
        return self._strategy.validate(value)

# ✅ 一個函式就夠了
def is_valid_email(value: str) -> bool:
    return "@" in value
```

**3. 預測未來需求：現在不需要的功能就不要寫**

```python
# ❌ 「以後可能需要支援多種格式」
def export_data(data: list, fmt: str = "json") -> str:
    if fmt == "json":
        return json.dumps(data)
    elif fmt == "csv":
        ...  # 目前沒有人用 CSV
    elif fmt == "xml":
        ...  # 目前沒有人用 XML
    else:
        raise ValueError(f"不支援的格式: {fmt}")

# ✅ 只做目前需要的
def export_data_as_json(data: list) -> str:
    return json.dumps(data)
```

**4. 過度防禦：不需要驗證不可能發生的情況**

```python
# ❌ 在內部函式中做多餘的防禦
def _calculate_total(items: list[OrderItem]) -> float:
    if items is None:  # 呼叫者已經確保不為 None
        raise ValueError("items 不可為 None")
    if not isinstance(items, list):  # 有型別標註就夠了
        raise TypeError("items 必須是 list")
    return sum(item.price * item.quantity for item in items)

# ✅ 信任內部呼叫者和型別系統
def _calculate_total(items: list[OrderItem]) -> float:
    return sum(item.price * item.quantity for item in items)
```

**5. 過度包裝第三方套件**

```python
# ❌ 用 wrapper 包住每個第三方 API
class HttpClient:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient()

    async def get(self, url: str) -> dict:
        response = await self._client.get(url)
        return response.json()

# ✅ 直接使用，除非你確實需要統一多個 HTTP 庫的介面
async with httpx.AsyncClient() as client:
    response = await client.get(url)
    data = response.json()
```

### 何時該抽象？

| 條件 | 行動 |
|------|------|
| 邏輯只出現 1 次 | 不要抽象，保持 inline |
| 邏輯出現 2 次 | 考慮是否真的相同，通常先容忍重複 |
| 邏輯出現 3 次以上 | 抽取為函式或類別（Rule of Three） |
| 有明確的多型需求 | 使用 Protocol 或 ABC |
| 只是「覺得以後可能需要」 | **不要做** |

## 常見陷阱

❌ **不要** 使用 `any` 型別或省略型別標註
✅ **要** 明確定義所有函式參數和回傳值的型別

❌ **不要** 在非同步程式中循序執行可並行的操作
✅ **要** 使用 `asyncio.gather()` 並行執行獨立操作

❌ **不要** 使用魔術數字
✅ **要** 定義有意義的常數名稱

❌ **不要** 巢狀超過 3 層
✅ **要** 使用 early return 減少巢狀

❌ **不要** 使用 `datetime.now()` （naive datetime，無時區資訊）
✅ **要** 使用 `datetime.now(timezone.utc)` 明確指定時區

❌ **不要** 在 logging 中使用 f-string（`logger.debug(f"user {uid}")`）
✅ **要** 使用 `%` 格式化（`logger.debug("user %s", uid)`），延遲求值避免效能浪費

## 最佳實踐

- **命名**：動詞-名詞模式（`fetch_user`、`calculate_score`）
- **函式**：保持短小（< 50 行），單一職責
- **錯誤**：捕獲特定例外，提供有意義的錯誤訊息
- **測試**：使用 AAA 模式（Arrange-Act-Assert）
- **效能**：使用 `@lru_cache` 快取昂貴計算，生成器處理大型資料
- **資源**：使用 `with` 語句管理資源（檔案、連線）

## 工具鏈

| 工具 | 用途 | 指令 |
|------|------|------|
| `ruff` | Linting + import 排序 + 格式化 | `ruff check --fix && ruff format` |
| `mypy` | 靜態型別檢查 | `mypy --strict` |
| `pytest` | 測試 | `pytest -v` |

建議在 CI 和 pre-commit hook 中整合以上工具。

## 範例檔案

- **examples/** - 詳細程式碼範例：
  - `naming_conventions.py` - 命名規範與變數/函式/類別範例
  - `error_handling.py` - 完整的錯誤處理模式
  - `async_patterns.py` - 非同步程式設計模式
  - `type_annotations.py` - 型別標註與資料模型
  - `testing_patterns.py` - pytest 測試模式與 fixtures
  - `api_design.py` - FastAPI 端點設計模式
