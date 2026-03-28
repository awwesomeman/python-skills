"""
examples/api_design.py

FastAPI 端點設計：統一回應格式、Request/Response 分離、依賴注入、錯誤處理。
輸入層：HTTP 請求（FastAPI Router）；輸出層：UserService → UserRepository。
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Annotated, Any, Generic, TypeVar

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)

T = TypeVar("T")


# ============================================================================
# 統一回應格式
# ============================================================================

class ApiResponse(BaseModel, Generic[T]):
    """統一的 API 回應格式。"""
    success: bool
    data: T | None = None
    error: str | None = None
    meta: dict[str, Any] | None = None


class PaginationMeta(BaseModel):
    """分頁資訊。"""
    total: int
    page: int
    limit: int
    total_pages: int


def success_response(data: T, meta: dict | None = None) -> ApiResponse[T]:
    """建立成功回應。"""
    return ApiResponse(success=True, data=data, meta=meta)


def error_response(message: str) -> ApiResponse[None]:
    """建立錯誤回應。"""
    return ApiResponse(success=False, error=message)


# ============================================================================
# 資料模型：Request / Response 分離
# ============================================================================

# --- Domain Model ---

@dataclass
class User:
    """使用者領域模型。"""
    id: str
    email: str
    name: str
    password_hash: str  # 內部使用，不應暴露
    is_active: bool
    created_at: datetime


# --- Request Models ---

class CreateUserRequest(BaseModel):
    """建立使用者請求。"""
    email: str = Field(..., min_length=5, max_length=255, examples=["user@example.com"])
    name: str = Field(..., min_length=1, max_length=100, examples=["John Doe"])
    password: str = Field(..., min_length=8, examples=["securepassword123"])


class UpdateUserRequest(BaseModel):
    """更新使用者請求（部分更新）。"""
    name: str | None = Field(None, min_length=1, max_length=100)
    email: str | None = Field(None, min_length=5, max_length=255)


# --- Response Models ---

class UserResponse(BaseModel):
    """使用者回應（不含敏感資訊）。"""
    id: str
    email: str
    name: str
    is_active: bool
    created_at: datetime

    @classmethod
    def from_domain(cls, user: User) -> "UserResponse":
        """從領域模型轉換。"""
        return cls(
            id=user.id,
            email=user.email,
            name=user.name,
            is_active=user.is_active,
            created_at=user.created_at,
        )


class UserListResponse(BaseModel):
    """使用者列表回應。"""
    users: list[UserResponse]


# ============================================================================
# 依賴注入
# ============================================================================

class UserRepository:
    """使用者資料存取層。"""

    async def find_by_id(self, user_id: str) -> User | None:
        """根據 ID 查找使用者。"""
        raise NotImplementedError

    async def find_all(self, limit: int, offset: int) -> tuple[list[User], int]:
        """查找所有使用者，返回 (使用者列表, 總數)。"""
        raise NotImplementedError

    async def save(self, user: User) -> None:
        """儲存使用者。"""
        raise NotImplementedError


class UserNotFoundError(Exception):
    """使用者不存在錯誤（領域例外）。"""

    def __init__(self, user_id: str) -> None:
        super().__init__(f"使用者不存在: {user_id}")
        self.user_id = user_id


class UserService:
    """使用者服務層。

    注意：Service 層不應依賴 HTTP 概念（如 HTTPException），
    應拋出領域例外，由路由層轉換為 HTTP 回應。
    """

    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def get_user(self, user_id: str) -> User:
        """取得使用者，不存在時拋出領域例外。"""
        user = await self._repository.find_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        return user

    async def list_users(self, page: int, limit: int) -> tuple[list[User], int]:
        """列出使用者。"""
        offset = (page - 1) * limit
        return await self._repository.find_all(limit=limit, offset=offset)


# --- 依賴注入函式 ---

async def get_repository() -> UserRepository:
    """取得 Repository 實例。"""
    # 實際應用中會從 DI 容器取得
    raise NotImplementedError


async def get_user_service(
    repository: Annotated[UserRepository, Depends(get_repository)]
) -> UserService:
    """取得 Service 實例。"""
    return UserService(repository)


# ============================================================================
# API 路由
# ============================================================================

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get(
    "",
    response_model=ApiResponse[UserListResponse],
    summary="列出所有使用者",
    description="取得使用者列表，支援分頁。",
)
async def list_users(
    service: Annotated[UserService, Depends(get_user_service)],
    page: Annotated[int, Query(ge=1, description="頁碼")] = 1,
    limit: Annotated[int, Query(ge=1, le=100, description="每頁數量")] = 10,
) -> ApiResponse[UserListResponse]:
    """列出所有使用者。"""
    users, total = await service.list_users(page=page, limit=limit)

    return success_response(
        data=UserListResponse(
            users=[UserResponse.from_domain(u) for u in users]
        ),
        meta={
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit,
        },
    )


@router.get(
    "/{user_id}",
    response_model=ApiResponse[UserResponse],
    summary="取得單一使用者",
    responses={
        404: {"description": "使用者不存在"},
    },
)
async def get_user(
    user_id: str,
    service: Annotated[UserService, Depends(get_user_service)],
) -> ApiResponse[UserResponse]:
    """取得單一使用者。"""
    try:
        user = await service.get_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    return success_response(data=UserResponse.from_domain(user))


@router.post(
    "",
    response_model=ApiResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="建立使用者",
    responses={
        400: {"description": "驗證錯誤"},
        409: {"description": "Email 已存在"},
    },
)
async def create_user(
    request: CreateUserRequest,
    service: Annotated[UserService, Depends(get_user_service)],
) -> ApiResponse[UserResponse]:
    """建立新使用者。"""
    # 實作建立邏輯...
    raise NotImplementedError


@router.patch(
    "/{user_id}",
    response_model=ApiResponse[UserResponse],
    summary="更新使用者",
    responses={
        404: {"description": "使用者不存在"},
    },
)
async def update_user(
    user_id: str,
    request: UpdateUserRequest,
    service: Annotated[UserService, Depends(get_user_service)],
) -> ApiResponse[UserResponse]:
    """部分更新使用者。"""
    # 實作更新邏輯...
    raise NotImplementedError


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="刪除使用者",
    responses={
        404: {"description": "使用者不存在"},
    },
)
async def delete_user(
    user_id: str,
    service: Annotated[UserService, Depends(get_user_service)],
) -> None:
    """刪除使用者。"""
    # 實作刪除邏輯...
    raise NotImplementedError


# ============================================================================
# 錯誤處理中間件
# ============================================================================

def create_app() -> FastAPI:
    """建立 FastAPI 應用。"""
    app = FastAPI(
        title="User API",
        version="1.0.0",
        description="使用者管理 API",
    )

    # WHY: 全域攔截確保所有錯誤都返回統一的 ApiResponse 格式，前端只需處理一種結構
    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request,
        exc: HTTPException,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(exc.detail).model_dump(),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logger.exception("未處理的錯誤")

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response("內部伺服器錯誤").model_dump(),
        )

    app.include_router(router)
    return app


# ============================================================================
# 輸入驗證範例
# ============================================================================

class CreateOrderRequest(BaseModel):
    """建立訂單請求（含複雜驗證）。"""
    user_id: str
    items: list[dict[str, Any]] = Field(..., min_length=1)
    shipping_address: str = Field(..., min_length=10)
    notes: str | None = Field(None, max_length=500)

    @field_validator("items")
    @classmethod
    def validate_items(cls, v: list) -> list:
        """驗證訂單項目。"""
        for i, item in enumerate(v):
            if "product_id" not in item:
                raise ValueError(f"項目 {i}: 缺少 product_id")
            if item.get("quantity", 0) <= 0:
                raise ValueError(f"項目 {i}: 數量必須大於 0")
            if item.get("price", 0) < 0:
                raise ValueError(f"項目 {i}: 價格不可為負")
        return v
