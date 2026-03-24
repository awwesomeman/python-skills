---
name: python-logging
description: Python logging 設定標準。當設定 logging、建立 config.py、新增 logger、或詢問 log 最佳實踐時使用。
---

# Python Logging 設定標準

## 何時使用此 Skill

- 建立新專案需要設定 logging
- 在模組中新增 logger
- 詢問 Python logging 最佳實踐
- 需要 JSON 格式 log 輸出
- 整合 OpenTelemetry

## 前置檢查（重要）

使用此 Skill 前，**必須**先執行以下步驟：

1. **讀取專案現有的 `config.py`**，檢查目前的 logging 設定
2. **逐項比對**以下關鍵設定是否與本 Skill 推薦的方式一致：
   - `setup_logging()` 函數的實作邏輯（建立 StreamHandler、設定 Formatter、stdout 輸出）
   - `_get_formatter()` 的 JSON 格式定義（rename_fields 欄位映射）
   - 環境變數（`DEBUG`）的讀取方式與預設值
   - 模組層級是否呼叫 `setup_logging()`
3. **若發現不一致**，必須先向使用者說明差異內容，並詢問是否要更新為本 Skill 推薦的設定方式，取得同意後才能修改
4. **若完全一致**，告知使用者目前設定已符合標準，無需變更

> 注意：不要跳過此檢查步驟直接套用範本覆蓋，避免意外覆蓋使用者的自訂邏輯（如自訂 Filter、額外 Handler 等）。

## 快速開始

### 1. 建立 config.py

複製下方程式碼到專案的 `config.py`：

```python
"""Logging 設定模組。

設計原則：
- 所有 log 輸出到 stdout：容器環境中由 K8s 負責收集標準輸出，不使用檔案 logging
- 統一使用 JSON 格式：結構化輸出便於 GCP Cloud Logging 解析為 jsonPayload，支援欄位查詢
- 設定 root logger：單一設定點控制所有模組的 log 行為，各模組只需 getLogger(__name__)
- 模組層級執行 setup_logging()：透過 import 觸發初始化，確保在任何 log 呼叫前完成設定
- OTel 相容：僅依賴 opentelemetry-api，SDK 由 K8s OTel Operator 透過 annotation 自動注入
  使用 addHandler() 新增 handler，不會移除 OTel 注入的既有 handler
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
    root_logger.addHandler(handler)


setup_logging()
```

### 2. 在模組中使用

```python
import logging

logger = logging.getLogger(__name__)

logger.info("訊息")
logger.error("錯誤")
logger.exception("例外")  # 自動包含 traceback
```

## 環境變數

| 變數 | 預設值 | 說明 |
|------|--------|------|
| `DEBUG` | `False` | `True` 時 log level 為 DEBUG |

## 核心規則

1. **設定 root logger** - 在 `config.py` 中設定一次
2. **使用 named logger** - 各模組用 `logging.getLogger(__name__)`
3. **使用 % 格式化** - `logger.info("user %s", user_id)` 而非 f-string
4. **例外用 exception()** - 自動包含 traceback

## 輸出格式

**JSON 格式**
統一使用 JSON 格式輸出，GCP Cloud Logging 會自動將 JSON 解析為 `jsonPayload`，支援欄位查詢如 `jsonPayload.level="ERROR"`。
```json
{"asctime": "2024-01-15T10:30:45+0800", "level": "INFO", "logger": "myapp.service", "function": "main", "line": 42, "message": "訊息"}
```

欄位映射透過 `rename_fields` 參數完成：
- `levelname` → `level`
- `name` → `logger`
- `funcName` → `function`
- `lineno` → `line`

## 依賴套件

```bash
pip install python-json-logger
```

## OpenTelemetry 相容性

此設定與 OpenTelemetry auto-instrumentation 完全相容：

- **使用 `addHandler()` 新增 handler**：不會移除 OTel 注入的既有 handler，確保 OTel 的 log 處理正常運作
- **明確輸出到 stdout**：指定 `sys.stdout`，確保 log 總是輸出到標準輸出
- **僅依賴 opentelemetry-api**：SDK 由 K8s OTel Operator 透過 annotation 自動注入，不需在應用程式中安裝 SDK
- **完整 trace 關聯**：OTel 會自動將 trace_id、span_id 注入到 log 中
