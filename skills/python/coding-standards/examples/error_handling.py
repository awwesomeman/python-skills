"""錯誤處理模式範例

展示 Python 錯誤處理的最佳實踐。
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Awaitable, Callable, TypeVar

import httpx

logger = logging.getLogger(__name__)

T = TypeVar("T")


# ============================================================================
# 基本錯誤處理：捕獲特定例外
# ============================================================================

async def fetch_data(url: str) -> dict[str, Any]:
    """取得遠端資料，包含完整錯誤處理。

    Args:
        url: 目標 URL

    Returns:
        解析後的 JSON 資料

    Raises:
        ValueError: 當請求失敗或回應無效時
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        logger.error("HTTP 錯誤 %s: %s", e.response.status_code, e.response.text)
        raise ValueError(f"請求失敗: HTTP {e.response.status_code}") from e

    except httpx.TimeoutException as e:
        logger.error("請求超時: %s", url)
        raise ValueError("請求超時，請稍後重試") from e

    except httpx.RequestError as e:
        logger.error("網路錯誤: %s", e)
        raise ValueError("網路連線失敗") from e


# ============================================================================
# 自訂例外類別
# ============================================================================

class DomainError(Exception):
    """領域錯誤基底類別。"""

    def __init__(self, message: str, code: str | None = None) -> None:
        super().__init__(message)
        self.code = code


class ValidationError(DomainError):
    """驗證錯誤。"""

    def __init__(self, field: str, message: str) -> None:
        super().__init__(f"{field}: {message}", code="VALIDATION_ERROR")
        self.field = field


class NotFoundError(DomainError):
    """資源不存在錯誤。"""

    def __init__(self, resource: str, identifier: str) -> None:
        super().__init__(
            f"{resource} 不存在: {identifier}",
            code="NOT_FOUND"
        )
        self.resource = resource
        self.identifier = identifier


class AuthorizationError(DomainError):
    """授權錯誤。"""

    def __init__(self, action: str) -> None:
        super().__init__(f"無權限執行: {action}", code="UNAUTHORIZED")
        self.action = action


# ============================================================================
# 使用自訂例外
# ============================================================================

async def get_user(user_id: str) -> dict:
    """取得使用者，示範自訂例外使用。"""
    if not user_id:
        raise ValidationError("user_id", "不可為空")

    user = await _fetch_user_from_db(user_id)

    if user is None:
        raise NotFoundError("User", user_id)

    return user


async def _fetch_user_from_db(user_id: str) -> dict | None:
    """模擬從資料庫取得使用者。"""
    return None  # 模擬不存在


# ============================================================================
# 重試模式：指數退避
# ============================================================================


async def retry_with_backoff(
    operation: Callable[[], Awaitable[T]],
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,),
) -> T:
    """使用指數退避重試操作。

    Args:
        operation: 要執行的非同步操作
        max_retries: 最大重試次數
        base_delay: 基礎延遲秒數
        max_delay: 最大延遲秒數
        retryable_exceptions: 可重試的例外類型

    Returns:
        操作結果

    Raises:
        Exception: 當所有重試都失敗時
    """
    last_exception: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            return await operation()

        except retryable_exceptions as e:
            last_exception = e

            if attempt == max_retries:
                logger.error("所有重試都失敗 (%d 次嘗試)", max_retries + 1)
                raise

            # 計算指數退避延遲
            delay = min(base_delay * (2 ** attempt), max_delay)
            logger.warning(
                "操作失敗，%.1f 秒後重試 (嘗試 %d/%d)",
                delay, attempt + 1, max_retries + 1,
            )
            await asyncio.sleep(delay)

    # 不應該到達這裡，但為了型別安全
    raise last_exception or RuntimeError("重試邏輯錯誤")


# 使用範例
async def fetch_with_retry(url: str) -> dict:
    """帶重試的資料取得。"""
    return await retry_with_backoff(
        lambda: fetch_data(url),
        max_retries=3,
        base_delay=1.0,
        retryable_exceptions=(ValueError,),
    )


# ============================================================================
# Context Manager 錯誤處理
# ============================================================================


@asynccontextmanager
async def managed_transaction(connection) -> AsyncGenerator[None, None]:
    """管理資料庫交易，確保正確提交或回滾。"""
    try:
        yield
        await connection.commit()
    except Exception:
        await connection.rollback()
        raise


# 使用範例
async def transfer_money(from_account: str, to_account: str, amount: float) -> None:
    """轉帳範例，展示交易管理。"""
    connection = await get_db_connection()

    async with managed_transaction(connection):
        await deduct_balance(from_account, amount)
        await add_balance(to_account, amount)
        # 如果任何操作失敗，整個交易會回滾


async def get_db_connection():
    """模擬取得資料庫連線。"""
    pass


async def deduct_balance(account: str, amount: float) -> None:
    """模擬扣款。"""
    pass


async def add_balance(account: str, amount: float) -> None:
    """模擬加款。"""
    pass


# ============================================================================
# Early Return 模式：減少巢狀
# ============================================================================

async def process_order(order: dict, user: dict) -> dict:
    """處理訂單，使用 early return 減少巢狀。"""
    # ✅ 良好：使用 early return
    if not order:
        raise ValidationError("order", "訂單不可為空")

    if not user:
        raise AuthorizationError("處理訂單")

    if not user.get("is_active"):
        raise AuthorizationError("帳號已停用")

    if order.get("status") != "pending":
        raise ValidationError("order.status", "只能處理待處理訂單")

    # 所有驗證通過，執行主要邏輯
    return await _execute_order_processing(order)


async def _execute_order_processing(order: dict) -> dict:
    """執行訂單處理邏輯。"""
    return {"status": "processed", "order_id": order.get("id")}


# ❌ 不佳：過深巢狀
# async def process_order_bad(order, user):
#     if order:
#         if user:
#             if user.get("is_active"):
#                 if order.get("status") == "pending":
#                     return await _execute_order_processing(order)
#                 else:
#                     raise ValidationError(...)
#             else:
#                 raise AuthorizationError(...)
#         else:
#             raise AuthorizationError(...)
#     else:
#         raise ValidationError(...)
