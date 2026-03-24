"""命名規範範例

展示 Python 命名慣例與最佳實踐。
"""

# ============================================================================
# 常數：SCREAMING_SNAKE_CASE
# ============================================================================

MAX_RETRIES = 3
DEFAULT_TIMEOUT_SECONDS = 30
API_BASE_URL = "https://api.example.com"
DEBOUNCE_DELAY_MS = 500


# ============================================================================
# 變數：snake_case，描述性名稱
# ============================================================================

# ✅ 良好：描述性名稱
market_search_query = "election"
is_user_authenticated = True
total_revenue = 1000
retry_count = 0

# ❌ 不佳：不清楚的名稱
# q = "election"
# flag = True
# x = 1000


# ============================================================================
# 函式：snake_case，動詞-名詞模式
# ============================================================================

# ✅ 良好：動詞-名詞模式，清晰表達意圖
async def fetch_market_data(market_id: str) -> dict:
    """取得市場資料。"""
    pass


def calculate_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    """計算兩個向量的相似度。"""
    pass


def is_valid_email(email: str) -> bool:
    """檢查 email 格式是否有效。"""
    pass


def parse_json_response(response: str) -> dict:
    """解析 JSON 回應。"""
    pass


# ❌ 不佳：不清楚或僅名詞
# async def market(id): ...
# def similarity(a, b): ...
# def email(e): ...


# ============================================================================
# 類別：PascalCase
# ============================================================================

class MarketService:
    """市場服務類別。"""

    def __init__(self, api_client: "ApiClient") -> None:
        self._api_client = api_client

    async def get_market(self, market_id: str) -> "Market":
        """取得單一市場。"""
        pass

    async def list_active_markets(self) -> list["Market"]:
        """列出所有活躍市場。"""
        pass


class UserRepository:
    """使用者資料存取層。"""
    pass


class OrderProcessingError(Exception):
    """訂單處理錯誤。"""
    pass


# ============================================================================
# 私有成員：單底線前綴
# ============================================================================

class DataProcessor:
    """資料處理器範例。"""

    def __init__(self) -> None:
        self._cache: dict = {}  # 私有屬性
        self._is_initialized = False

    def process(self, data: list) -> list:
        """公開方法。"""
        validated = self._validate_data(data)
        return self._transform_data(validated)

    def _validate_data(self, data: list) -> list:
        """私有方法：驗證資料。"""
        return [item for item in data if item is not None]

    def _transform_data(self, data: list) -> list:
        """私有方法：轉換資料。"""
        return [self._process_single_item(item) for item in data]

    def _process_single_item(self, item) -> dict:
        """私有方法：處理單一項目。"""
        return {"processed": item}


# ============================================================================
# 布林變數：is_/has_/can_/should_ 前綴
# ============================================================================

is_active = True
is_user_logged_in = False
has_permission = True
has_valid_subscription = False
can_edit = True
can_delete = False
should_retry = True
should_send_notification = False
