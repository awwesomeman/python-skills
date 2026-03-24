"""測試模式範例

展示 pytest 測試的最佳實踐。
"""

from dataclasses import dataclass
from datetime import datetime
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ============================================================================
# 被測試的程式碼（範例）
# ============================================================================

@dataclass
class User:
    """使用者資料類別。"""
    id: str
    email: str
    name: str
    is_active: bool = True


class UserService:
    """使用者服務。"""

    def __init__(self, repository: "UserRepository") -> None:
        self._repository = repository

    async def get_user(self, user_id: str) -> User | None:
        """取得使用者。"""
        return await self._repository.find_by_id(user_id)

    async def create_user(self, email: str, name: str) -> User:
        """建立使用者。"""
        if await self._repository.find_by_email(email):
            raise ValueError("Email 已存在")

        user = User(
            id=f"user_{datetime.now().timestamp()}",
            email=email,
            name=name,
        )
        await self._repository.save(user)
        return user


class UserRepository:
    """使用者資料存取層（介面）。"""

    async def find_by_id(self, user_id: str) -> User | None:
        raise NotImplementedError

    async def find_by_email(self, email: str) -> User | None:
        raise NotImplementedError

    async def save(self, user: User) -> None:
        raise NotImplementedError


# ============================================================================
# Fixtures：測試資料與依賴
# ============================================================================

@pytest.fixture
def sample_user() -> User:
    """提供範例使用者。"""
    return User(
        id="user_123",
        email="test@example.com",
        name="Test User",
        is_active=True,
    )


@pytest.fixture
def inactive_user() -> User:
    """提供停用的使用者。"""
    return User(
        id="user_456",
        email="inactive@example.com",
        name="Inactive User",
        is_active=False,
    )


@pytest.fixture
def mock_repository() -> MagicMock:
    """提供 Mock 的 Repository。"""
    repo = MagicMock(spec=UserRepository)
    repo.find_by_id = AsyncMock(return_value=None)
    repo.find_by_email = AsyncMock(return_value=None)
    repo.save = AsyncMock()
    return repo


@pytest.fixture
def user_service(mock_repository: MagicMock) -> UserService:
    """提供 UserService 實例。"""
    return UserService(mock_repository)


# ============================================================================
# 基本測試：AAA 模式（Arrange-Act-Assert）
# ============================================================================

class TestUserService:
    """UserService 測試。"""

    @pytest.mark.asyncio
    async def test_get_user_returns_user_when_exists(
        self,
        user_service: UserService,
        mock_repository: MagicMock,
        sample_user: User,
    ) -> None:
        """當使用者存在時，應返回使用者。"""
        # Arrange（準備）
        mock_repository.find_by_id.return_value = sample_user

        # Act（執行）
        result = await user_service.get_user("user_123")

        # Assert（驗證）
        assert result == sample_user
        mock_repository.find_by_id.assert_called_once_with("user_123")

    @pytest.mark.asyncio
    async def test_get_user_returns_none_when_not_exists(
        self,
        user_service: UserService,
        mock_repository: MagicMock,
    ) -> None:
        """當使用者不存在時，應返回 None。"""
        # Arrange
        mock_repository.find_by_id.return_value = None

        # Act
        result = await user_service.get_user("nonexistent")

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_create_user_success(
        self,
        user_service: UserService,
        mock_repository: MagicMock,
    ) -> None:
        """成功建立使用者。"""
        # Arrange
        mock_repository.find_by_email.return_value = None

        # Act
        result = await user_service.create_user(
            email="new@example.com",
            name="New User",
        )

        # Assert
        assert result.email == "new@example.com"
        assert result.name == "New User"
        assert result.is_active is True
        mock_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_raises_error_when_email_exists(
        self,
        user_service: UserService,
        mock_repository: MagicMock,
        sample_user: User,
    ) -> None:
        """當 Email 已存在時，應拋出錯誤。"""
        # Arrange
        mock_repository.find_by_email.return_value = sample_user

        # Act & Assert
        with pytest.raises(ValueError, match="Email 已存在"):
            await user_service.create_user(
                email="test@example.com",
                name="Another User",
            )


# ============================================================================
# 參數化測試
# ============================================================================

@pytest.mark.parametrize(
    "email,is_valid",
    [
        ("valid@example.com", True),
        ("user.name@domain.org", True),
        ("invalid-email", False),
        ("@nodomain.com", False),
        ("", False),
    ],
)
def test_email_validation(email: str, is_valid: bool) -> None:
    """測試 Email 驗證邏輯。"""
    result = is_valid_email(email)
    assert result == is_valid


def is_valid_email(email: str) -> bool:
    """簡單的 Email 驗證。"""
    return bool(email and "@" in email and not email.startswith("@"))


@pytest.mark.parametrize(
    "input_value,expected",
    [
        (0, 0),
        (1, 1),
        (2, 4),
        (3, 9),
        (-2, 4),
    ],
)
def test_square(input_value: int, expected: int) -> None:
    """測試平方計算。"""
    assert input_value ** 2 == expected


# ============================================================================
# 例外測試
# ============================================================================

def divide(a: float, b: float) -> float:
    """除法運算。"""
    if b == 0:
        raise ZeroDivisionError("除數不能為零")
    return a / b


def test_divide_by_zero_raises_error() -> None:
    """除以零應拋出錯誤。"""
    with pytest.raises(ZeroDivisionError, match="除數不能為零"):
        divide(10, 0)


def test_divide_success() -> None:
    """正常除法。"""
    result = divide(10, 2)
    assert result == 5.0


# ============================================================================
# Mock 與 Patch
# ============================================================================

async def fetch_user_from_api(user_id: str) -> dict:
    """從 API 取得使用者（需要 mock）。"""
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.example.com/users/{user_id}")
        return response.json()


@pytest.mark.asyncio
async def test_fetch_user_from_api() -> None:
    """測試 API 呼叫（使用 patch）。"""
    expected_user = {"id": "123", "name": "Test"}

    with patch("httpx.AsyncClient") as mock_client:
        # 設定 mock 行為
        mock_response = MagicMock()
        mock_response.json.return_value = expected_user

        mock_instance = MagicMock()
        mock_instance.get = AsyncMock(return_value=mock_response)
        mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
        mock_instance.__aexit__ = AsyncMock()

        mock_client.return_value = mock_instance

        # 執行
        result = await fetch_user_from_api("123")

        # 驗證
        assert result == expected_user


# ============================================================================
# Fixture Scope：控制 Fixture 生命週期
# ============================================================================

@pytest.fixture(scope="module")
def expensive_resource() -> Generator[str, None, None]:
    """模組級別的 fixture（整個模組只建立一次）。"""
    # Setup
    resource = "expensive_connection"
    yield resource
    # Teardown
    print("Cleaning up expensive resource")


@pytest.fixture(scope="function")
def per_test_resource() -> Generator[str, None, None]:
    """函式級別的 fixture（每個測試都建立）。"""
    # Setup
    resource = "per_test_resource"
    yield resource
    # Teardown（每個測試後執行）


# ============================================================================
# Async Fixtures
# ============================================================================

@pytest.fixture
async def async_db_session() -> AsyncGenerator[MagicMock, None]:
    """非同步資料庫 session fixture。"""
    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    yield session

    # 清理
    await session.rollback()


# ============================================================================
# 測試命名規範
# ============================================================================

# ✅ 良好：描述性測試名稱
def test_returns_empty_list_when_no_users_found() -> None:
    """當沒有使用者時返回空列表。"""
    pass


def test_raises_validation_error_when_email_invalid() -> None:
    """當 Email 無效時拋出驗證錯誤。"""
    pass


def test_creates_user_with_default_active_status() -> None:
    """建立使用者時預設為啟用狀態。"""
    pass


# ❌ 不佳：模糊的測試名稱
# def test_user(): ...
# def test_it_works(): ...
# def test_success(): ...
