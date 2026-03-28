"""
examples/over_engineering.py

過度開發反模式與專案結構：設計模式濫用、過度防禦、過度包裝、SRP、依賴注入。
輸入層：各種程式碼設計決策；輸出層：❌/✅ 對照寫法。
"""

from dataclasses import dataclass
from typing import Protocol

import httpx


# ============================================================
# 1. 不必要的設計模式：三行能解決的事不需要一個 class
# ============================================================

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


# ============================================================
# 2. 過度防禦：不需要驗證不可能發生的情況
# ============================================================


@dataclass
class OrderItem:
    price: float
    quantity: int


# ❌ 在內部函式中做多餘的防禦
def _calculate_total_bad(items: list[OrderItem]) -> float:
    if items is None:  # 呼叫者已經確保不為 None
        raise ValueError("items 不可為 None")
    if not isinstance(items, list):  # 有型別標註就夠了
        raise TypeError("items 必須是 list")
    return sum(item.price * item.quantity for item in items)


# ✅ 信任內部呼叫者和型別系統
def _calculate_total(items: list[OrderItem]) -> float:
    return sum(item.price * item.quantity for item in items)


# ============================================================
# 3. 過度包裝第三方套件
# ============================================================


# ❌ 用 wrapper 包住每個第三方 API
class HttpClient:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient()

    async def get(self, url: str) -> dict:
        response = await self._client.get(url)
        return response.json()


# ✅ 直接使用，除非你確實需要統一多個 HTTP 庫的介面
async def fetch_data(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()


# ============================================================
# 4. 違反單一職責原則 (SRP)
# ============================================================


# ❌ 一個函式同時做了資料獲取、計算、寫入
def process_data_bad(db) -> None:
    data = db.query("SELECT * FROM raw_data")
    result = sum(row["value"] for row in data)
    db.execute("INSERT INTO results VALUES (?)", (result,))


# ✅ 各自獨立，由呼叫端組合
def fetch_raw_data(db) -> list[dict]:
    return db.query("SELECT * FROM raw_data")


def compute_total(data: list[dict]) -> float:
    return sum(row["value"] for row in data)


def save_result(db, result: float) -> None:
    db.execute("INSERT INTO results VALUES (?)", (result,))


# 組合在呼叫端
# data = fetch_raw_data(db)
# total = compute_total(data)
# save_result(db, total)


# ============================================================
# 5. 依賴注入：硬編碼 vs 參數傳入
# ============================================================


class DatabaseClient:
    """示意用的 DB client。"""

    def save(self, order: dict) -> bool:
        return True


# WHY: 硬編碼 global 實例讓測試無法替換為 mock，且模組載入時就建立連線可能在 import 階段失敗
# ❌ 在函式內讀取 global 狀態，難以隔離測試
_global_db = DatabaseClient()


def process_order_bad(order: dict) -> bool:
    return _global_db.save(order)


# ✅ 相依物件透過參數傳入，可被測試替換 (Mock)
def process_order(order: dict, db_client: DatabaseClient) -> bool:
    return db_client.save(order)
