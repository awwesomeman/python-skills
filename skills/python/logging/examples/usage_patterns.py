"""Logger 使用模式範例

這個範例展示在應用程式各模組中使用 logger 的最佳實踐。
"""

import logging
from typing import Any

# =============================================================================
# 基本使用：在每個模組中取得專屬的 logger
# =============================================================================

# 使用 __name__ 讓 logger 名稱自動對應模組路徑
logger = logging.getLogger(__name__)


# =============================================================================
# 各種 Log Level 的使用時機
# =============================================================================


def log_level_examples() -> None:
    """各種 log level 的使用時機示範"""

    # DEBUG: 詳細的除錯資訊，只在開發或排查問題時啟用
    logger.debug("正在處理資料，count: %d", 100)

    # INFO: 一般性的資訊，記錄應用正常運作的重要事件
    logger.info("應用程式啟動完成")
    logger.info("處理完成，共 %d 筆資料", 1000)

    # WARNING: 警告，不影響功能但需要注意的情況
    logger.warning("設定檔使用預設值: %s", "timeout=30")

    # ERROR: 錯誤，功能無法正常執行但應用仍在運作
    logger.error("無法連接到資料庫: %s", "connection refused")

    # CRITICAL: 嚴重錯誤，可能導致應用無法繼續運作
    logger.critical("必要的設定檔遺失")


# =============================================================================
# 使用 extra 參數傳遞結構化資訊
# =============================================================================


def structured_logging_example() -> None:
    """使用 extra 參數記錄結構化資訊

    注意：extra 欄位在 JSON 格式中會直接出現，文字格式中不會顯示。
    """
    logger.info(
        "處理完成",
        extra={"task_id": "abc-123", "duration_ms": 150},
    )


# =============================================================================
# 例外處理
# =============================================================================


def exception_handling_example(data: dict[str, Any]) -> str | None:
    """例外處理時的 logging 模式"""

    try:
        result = data["key"]["nested"]
        return str(result)

    except KeyError:
        # logger.exception() 會自動記錄 traceback
        logger.exception("資料格式錯誤")
        return None

    except Exception:
        logger.exception("發生未預期錯誤")
        raise


# =============================================================================
# 避免常見錯誤
# =============================================================================


def common_mistakes() -> None:
    """常見錯誤與正確做法"""

    user_id = "user_123"

    # [錯誤] 使用 f-string - 即使 level 被過濾，仍會執行字串格式化
    # logger.debug(f"Processing {user_id}")

    # [正確] 使用 % 格式化 - logger 會在需要時才格式化
    logger.debug("Processing %s", user_id)

    # [錯誤] 記錄敏感資訊
    # logger.info("Password: %s", password)

    # [正確] 只記錄必要資訊
    logger.info("User %s authenticated", user_id)

    # [錯誤] 例外只記錄訊息，沒有 traceback
    # except Exception as e:
    #     logger.error("Error: %s", e)

    # [正確] 使用 exception() 自動包含 traceback
    # except Exception:
    #     logger.exception("Error occurred")
