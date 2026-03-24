---
name: jason-python-skills
description: Python 開發相關技能入口。當撰寫、審查、重構 Python 程式碼，或設定 logging 時使用。根據任務路由到對應的子 skill。
---

# Python 技能索引 (Python Skills Overview)

> 本 skill 是 Python 開發的入口。根據當前任務判斷應啟用哪個子 skill。

---

## 任務路由

| 任務 | 載入的 Skill |
|------|-------------|
| 撰寫 / 審查 / 重構 Python 程式碼 | coding-standards |
| 設定 logging / 建立 logger | logging |
| 新專案建置 | coding-standards + logging |

## Skill 簡表

| Skill | 定位 |
|-------|------|
| **coding-standards** | Python 編碼標準：命名慣例、錯誤處理、async、typing、測試規範 |
| **logging** | Python logging 設定標準：logger 建立、config 設定、log level 規範、最佳實踐 |
