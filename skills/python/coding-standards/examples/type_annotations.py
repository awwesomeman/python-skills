"""型別標註與資料模型範例

展示 Python 型別系統的最佳實踐。
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import (
    Any,
    Awaitable,
    Callable,
    Generic,
    Literal,
    NewType,
    Protocol,
    TypeAlias,
    TypeVar,
)

from pydantic import BaseModel, Field, field_validator


# ============================================================================
# 基本型別標註
# ============================================================================

def calculate_total(prices: list[float], tax_rate: float = 0.1) -> float:
    """計算含稅總價。

    Args:
        prices: 價格列表
        tax_rate: 稅率（預設 10%）

    Returns:
        含稅總價
    """
    subtotal = sum(prices)
    return subtotal * (1 + tax_rate)


def find_user(users: list[dict[str, Any]], user_id: str) -> dict[str, Any] | None:
    """查找使用者。

    Returns:
        使用者資料，若不存在則返回 None
    """
    for user in users:
        if user.get("id") == user_id:
            return user
    return None


# ============================================================================
# Enum：使用列舉取代字串常數
# ============================================================================

class MarketStatus(Enum):
    """市場狀態列舉。"""
    ACTIVE = auto()
    RESOLVED = auto()
    CLOSED = auto()
    CANCELLED = auto()


class OrderType(Enum):
    """訂單類型列舉。"""
    BUY = "buy"
    SELL = "sell"


# 使用範例
def process_order(order_type: OrderType, amount: float) -> dict:
    """處理訂單。"""
    if order_type == OrderType.BUY:
        return {"action": "buy", "amount": amount}
    return {"action": "sell", "amount": amount}


# ❌ 不佳：使用字串
# def process_order_bad(order_type: str, amount: float):
#     if order_type == "buy":  # 容易打錯
#         ...


# ============================================================================
# Dataclass：簡單資料結構
# ============================================================================

@dataclass
class User:
    """使用者資料類別。"""
    id: str
    email: str
    name: str
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)  # 不可變
class Coordinate:
    """座標（不可變）。"""
    x: float
    y: float


@dataclass
class Market:
    """市場資料類別。"""
    id: str
    name: str
    status: MarketStatus
    description: str = ""
    volume: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# ============================================================================
# Pydantic：API 輸入驗證
# ============================================================================

class CreateUserRequest(BaseModel):
    """建立使用者請求。"""
    email: str = Field(..., min_length=5, max_length=255)
    name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=8)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("無效的 email 格式")
        return v.lower()


class UpdateUserRequest(BaseModel):
    """更新使用者請求（所有欄位可選）。"""
    name: str | None = Field(None, min_length=1, max_length=100)
    email: str | None = Field(None, min_length=5, max_length=255)


class PaginationParams(BaseModel):
    """分頁參數。"""
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)


# ============================================================================
# Generic：泛型類別
# ============================================================================

T = TypeVar("T")


@dataclass
class ApiResponse(Generic[T]):
    """通用 API 回應格式。"""
    success: bool
    data: T | None = None
    error: str | None = None


# 使用範例
def get_user_response(user: User) -> ApiResponse[User]:
    """取得使用者回應。"""
    return ApiResponse(success=True, data=user)


def get_users_response(users: list[User]) -> ApiResponse[list[User]]:
    """取得使用者列表回應。"""
    return ApiResponse(success=True, data=users)


# ============================================================================
# Protocol：結構化型別（Duck Typing）
# ============================================================================

class Serializable(Protocol):
    """可序列化介面。"""

    def to_dict(self) -> dict[str, Any]: ...


class JsonSerializable(Protocol):
    """可 JSON 序列化介面。"""

    def to_json(self) -> str: ...


def save_to_file(obj: Serializable, path: str) -> None:
    """儲存可序列化物件到檔案。"""
    data = obj.to_dict()
    # 寫入檔案...


# 任何有 to_dict 方法的類別都可以傳入
@dataclass
class Config:
    """配置類別（實作 Serializable）。"""
    name: str
    value: str

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "value": self.value}


# ============================================================================
# Type Alias：型別別名
# ============================================================================

UserId = NewType("UserId", str)
MarketId = NewType("MarketId", str)

# 複雜型別的別名
JsonDict: TypeAlias = dict[str, Any]
Callback: TypeAlias = Callable[[str], None]
AsyncCallback: TypeAlias = Callable[[str], Awaitable[None]]


def get_user_by_id(user_id: UserId) -> User | None:
    """使用 NewType 增加型別安全。"""
    pass


# ============================================================================
# Literal：限定值型別
# ============================================================================

LogLevel = Literal["debug", "info", "warning", "error"]


def log_message(message: str, level: LogLevel = "info") -> None:
    """記錄訊息。"""
    print(f"[{level.upper()}] {message}")


# 只能傳入指定的值
# log_message("test", "invalid")  # 型別檢查會報錯


# ============================================================================
# 綜合範例：完整的領域模型
# ============================================================================

@dataclass
class OrderItem:
    """訂單項目。"""
    product_id: str
    quantity: int
    unit_price: float

    @property
    def total(self) -> float:
        """計算項目總價。"""
        return self.quantity * self.unit_price


@dataclass
class Order:
    """訂單。"""
    id: str
    user_id: UserId
    items: list[OrderItem]
    status: Literal["pending", "confirmed", "shipped", "delivered"]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def total(self) -> float:
        """計算訂單總價。"""
        return sum(item.total for item in self.items)

    def add_item(self, item: OrderItem) -> None:
        """新增項目。"""
        self.items.append(item)


class CreateOrderRequest(BaseModel):
    """建立訂單請求。"""
    items: list[dict[str, Any]] = Field(..., min_length=1)

    @field_validator("items")
    @classmethod
    def validate_items(cls, v: list) -> list:
        for item in v:
            if "product_id" not in item:
                raise ValueError("每個項目必須包含 product_id")
            if item.get("quantity", 0) <= 0:
                raise ValueError("數量必須大於 0")
        return v
