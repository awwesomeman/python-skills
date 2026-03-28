---
name: jason-python-skills
description: Python 開發相關技能入口。當撰寫、審查、重構 Python 程式碼，或設定 logging 時使用。根據任務路由到對應的子 skill。
---

# Python 技能索引 (Python Skills Overview)

> 本 skill 是 Python 開發的入口。根據當前任務判斷應啟用哪個子 skill。

---

## 任務路由

判斷任務類型後，以**本檔案所在目錄**為基準，**直接讀取**對應子目錄的 SKILL.md 並依照規範執行，不需要詢問使用者確認。若父層與子層規則衝突，以子層為準。

| 任務 | 載入的 Skill（相對於本目錄） |
|------|------|
| 撰寫 / 審查 / 重構 Python 程式碼 | [coding-standards/SKILL.md](./coding-standards/SKILL.md) |
| 設定 logging / 建立 logger | [logging/SKILL.md](./logging/SKILL.md) |
| 新專案建置 | [coding-standards/SKILL.md](./coding-standards/SKILL.md) + [logging/SKILL.md](./logging/SKILL.md) |

## Skill 簡表

| Skill | 定位 |
|-------|------|
| **coding-standards** | Python 編碼標準：命名慣例、錯誤處理、async、typing、測試規範 |
| **logging** | Python logging 設定標準：logger 建立、config 設定、log level 規範、最佳實踐 |
