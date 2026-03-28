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
2. **逐項比對**是否與本 Skill 推薦的方式一致（`setup_logging()` 邏輯、JSON Formatter、環境變數讀取）
3. **若發現不一致**，先向使用者說明差異，取得同意後才修改
4. **若完全一致**，告知使用者目前設定已符合標準，無需變更

> 不要跳過此檢查直接套用範本覆蓋，避免意外覆蓋使用者的自訂邏輯（如自訂 Filter、額外 Handler）。

## 設計原則

| 原則 | 做法 | 原因 |
|------|------|------|
| 設定 root logger | 在 `config.py` 中設定一次 | 單一設定點控制所有模組行為，避免各模組重複設定產生衝突 |
| 使用 named logger | 各模組用 `logging.getLogger(__name__)` | logger 名稱自動對應模組路徑，排查時能快速定位來源 |
| `%` 格式化 | `logger.info("user %s", uid)` 而非 f-string | f-string 在低等級日誌未輸出時仍會求值，浪費效能 |
| 例外用 `exception()` | 不要用 `error(str(e))` | `exception()` 自動附帶完整 traceback，`error()` 只記錄訊息 |
| 模組層級初始化 | `config.py` 底部直接呼叫 `setup_logging()` | 透過 import 觸發，確保在任何 log 呼叫前完成設定 |

> 完整 config.py 範本見 `examples/config_template.py`，使用方式見 `examples/usage_patterns.py`。

## 在模組中使用

```python
import logging

logger = logging.getLogger(__name__)

logger.info("訊息")
logger.exception("例外")  # 自動包含 traceback
```

## 環境變數

| 變數 | 預設值 | 說明 |
|------|--------|------|
| `DEBUG` | `False` | `True` 時 log level 為 DEBUG |

## 輸出格式

統一使用 **JSON 格式**。欄位映射透過 `rename_fields` 完成：

| 原始欄位 | 映射為 | 原因 |
|----------|--------|------|
| `levelname` | `level` | 對齊 GCP Cloud Logging `jsonPayload` 查詢慣例 |
| `name` | `logger` | 語意更明確 |
| `funcName` | `function` | 簡化欄位名 |
| `lineno` | `line` | 簡化欄位名 |

## 容器環境規範（K8s / GCP）

> 以下規則適用於容器化部署環境。本地開發或非容器環境可依需求調整。

- **所有 log 輸出到 stdout**：容器環境中由 K8s 負責收集標準輸出，不使用檔案 logging
- **JSON 格式輸出**：GCP Cloud Logging 自動將 JSON 解析為 `jsonPayload`，支援欄位查詢如 `jsonPayload.level="ERROR"`

## OpenTelemetry 相容性（K8s 環境）

> 僅適用於透過 K8s OTel Operator 進行 auto-instrumentation 的環境。

- **使用 `addHandler()` 新增 handler**：不會移除 OTel 注入的既有 handler
- **僅依賴 `opentelemetry-api`**：SDK 由 K8s OTel Operator 透過 annotation 自動注入
- **完整 trace 關聯**：OTel 會自動將 trace_id、span_id 注入到 log 中

## 依賴套件

```bash
pip install python-json-logger
```

## 提交前檢查清單

| 檢查項目 |
|----------|
| 使用 `logging.getLogger(__name__)` 而非手動命名？ |
| logging 使用 `%` 格式化而非 f-string？ |
| 例外處理使用 `logger.exception()` 而非 `logger.error()`？ |
| 沒有在模組中重複呼叫 `basicConfig()` 或自建 handler？ |
| 敏感資訊（密碼、token）沒有被記錄到 log？ |

## 範例檔案

| 檔案 | 內容 |
|------|------|
| `examples/config_template.py` | 完整 config.py 範本（root logger + JSON formatter） |
| `examples/usage_patterns.py` | Logger 使用模式（log level、結構化 log、例外處理） |
