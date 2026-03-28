"""
examples/config_template.py

Logging 設定範本：root logger 初始化、JSON formatter、環境變數控制。
輸入層：環境變數（DEBUG）；輸出層：stdout（JSON 格式）。
"""

import logging
import os
import sys

from pythonjsonlogger import jsonlogger


def _verify_bool_env_var(env_var: str, default: str = "False") -> bool:
    """驗證布林型環境變數。"""
    return os.getenv(env_var, default).lower() in ("true", "1", "t")


DEBUG: bool = _verify_bool_env_var("DEBUG")
LOGGER_LEVEL: int = logging.DEBUG if DEBUG else logging.INFO


def _get_formatter() -> logging.Formatter:
    """根據設定回傳對應的 Formatter。"""
    # WHY: rename_fields 讓欄位名稱對齊 GCP Cloud Logging 的 jsonPayload 查詢慣例
    return jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(funcName)s %(lineno)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
        rename_fields={
            "levelname": "level",
            "name": "logger",
            "funcName": "function",
            "lineno": "line",
        },
    )


def setup_logging() -> None:
    """設定 root logger。"""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_get_formatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(LOGGER_LEVEL)
    # WHY: 用 addHandler 而非 basicConfig，避免覆蓋 OTel Operator 注入的既有 handler
    root_logger.addHandler(handler)


# WHY: 模組層級執行，透過 import 觸發初始化，確保在任何 log 呼叫前完成設定
setup_logging()
