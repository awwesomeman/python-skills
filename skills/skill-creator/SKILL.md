---
name: jason-skill-creator
description: Guidelines for designing and writing Claude skills. Use when creating new skills, refactoring existing skills, reviewing skill quality, or deciding how to structure a skill project. Also use when asking "should this be a skill?", "how to split skills?", or "is this skill too long/complex?".
---

# Skill 開發指南 (Skill Creator Guidelines)

> Skill 的目的是壓縮專家判斷力，而非取代程式碼生成能力。

## 1. Skill 是什麼？

Skill = **判斷力壓縮包 (Judgment Compression Pack)**

AI agent 已經會寫程式碼。它缺的是：
- 哪些地方有隱藏陷阱？
- 業界資深人士會怎麼做？
- 什麼情況下「看起來對」但其實會出事？

Skill 的價值在於提供這些 **principles + pitfalls**，讓 agent 做出更好的決策。

---

## 2. 黃金比例：80/20

| 內容類型 | 比例 | 說明 |
|----------|------|------|
| 原則與陷阱 | 80% | 判斷準則、常見錯誤、何時用什麼、為什麼 |
| 程式碼範例 | 20% | 僅用於展示「陷阱的正確寫法」或「容易寫錯的 pattern」 |

### 程式碼範例的使用時機

**應該放程式碼的情況：**
- 正確寫法與錯誤寫法差異微妙（如 CUSUM 遞迴 vs `cumsum().clip()`）— 因為文字描述不足以傳達差異
- API 呼叫方式不直覺（如 `join_asof(strategy="backward")`）— 因為 agent 可能猜錯參數
- 一行程式碼能取代一段文字解釋

**不應該放程式碼的情況：**
- 完整函數實作 — agent 會自己寫，放進來只是佔 context window
- 標準 library 用法 — agent 已經知道
- 可以用一句話描述的邏輯

## 3. 結構設計原則

### 3.1 層級架構（多 skill 專案）

當一個領域有多個相關 skill 時，用父子架構組織。單一獨立 skill 不需要這層結構。

```
domain/
├── SKILL.md          ← 入口：pipeline 流向、skill 路由表、通用原則
├── sub-skill-a/
│   └── SKILL.md      ← 專注於該層的原則與陷阱
└── sub-skill-b/
    └── SKILL.md
```

- **父層 SKILL.md**：負責路由（何時用哪個子 skill）與跨層通用原則
- **子層 SKILL.md**：專注於該領域的判斷準則，不重複父層內容

### 3.2 路由表（多 skill 專案）

父層應包含明確的路由表，標示每個子 skill「何時使用」與「何時不要使用」。沒有路由表時，agent 面對多個相關 skill 會猶豫或選錯，浪費 context 載入不相關的 skill。

路由表必須包含以下四要素，否則 agent 會反問使用者或路徑解析失敗：

| 要素 | 範例 | 原因 |
|------|------|------|
| **指令句** | 「直接讀取...不需要詢問使用者確認」 | 沒有明確指令時 agent 會反問而非行動 |
| **路徑基準** | 「以本檔案所在目錄為基準」 | 防止 agent 用使用者 CWD 拼出錯誤路徑 |
| **相對 Markdown 連結** | `[x/SKILL.md](./x/SKILL.md)`（禁止絕對路徑） | 讓 parser 建立依賴圖；絕對路徑會導致跨機器/CI 失效 |
| **Override 聲明** | 「子層規則優先」 | 消除父子衝突時 agent 的幻覺風險 |

### 3.3 examples/ 目錄模式

當程式碼範例超過 3 行或有多組 ❌/✅ 對照時，移到 `examples/` 目錄，SKILL.md 只留一句話規則 + 「詳見 `examples/xxx.py`」。這是落實 80/20 比例的關鍵手段。

- examples 檔案必須**遵守自身 skill 的規範**（吃自己的狗食）— 否則範例本身就是反面教材
- examples 檔頭加模組級架構定位說明（輸入層/輸出層），幫助 agent 快速理解檔案在系統中的角色

### 3.4 Cross-cutting 規範（多 skill 專案）

適用於所有子 skill 的規範（如 coding standards）應獨立為一個 skill，並在 description 中標明 cross-cutting 性質。這避免同一條規則散落在多個 skill 中，修改時遺漏。

## 4. 撰寫原則

### 4.1 每條規則都要有「為什麼」

不要只寫「禁止 X」，要寫「禁止 X，因為 Y 會導致 Z」。Agent 理解原因後，能在邊界情境做出正確判斷，而非機械式套用規則。

### 4.2 標記適用範圍

如果某些規則只適用於特定情境，明確標記（如 `(通用)` vs `(截面策略)`）。不標記時，agent 會在不適用的情境中強行套用規則，產出不合理的程式碼。

### 4.3 提交前檢查清單

建議在 skill 結尾放檢查表 — 對抗 agent 生成大量程式碼後的**注意力衰減**，確保關鍵規則沒有被跳過。

| 情境 | 建議 |
|------|------|
| 指導程式碼生成的 skill | 建議有 — agent 產出越多，遺漏風險越高 |
| 不可逆動作（commit、deploy） | 強烈建議 — 執行後無法撤回，checklist 是最後 gate |
| 純路由的 parent skill | 不需要 — 沒有需要檢查的產出物 |

格式依用途選擇：分類檢查用表格（如按 look-ahead / 統計 / 效能分欄），序列 gate 用 task list `- [ ]`。

### 4.4 精簡優先

- 單一 skill 控制在 100 行以內（理想值），不超過 150 行 — 超過此長度 agent 的注意力會被稀釋，重要規則被淹沒在細節中
- 刪掉 agent 能從 context 推斷的內容
- 用表格取代冗長的條件描述

## 5. 常見反模式 (Anti-patterns)

| 反模式 | 後果 | 修正 |
|--------|------|------|
| **把 Skill 當 Library**：放入完整函數實作 | agent 直接複製貼上，失去彈性、佔用 context | 只保留 1-3 行關鍵 pattern，完整實作讓 agent 自己寫 |
| **重複定義**：同一概念散落多個 skill | 修改時遺漏，產生矛盾版本 | 只在一個 skill 定義，其他用交叉引用 |
| **過度規範**：把所有邊界情境都寫成硬性規則 | agent 抓不到重點，注意力被稀釋 | 只規範「違反後果嚴重」的事項，輕微偏好用「建議」 |
| **缺少路由**：多 skill 但沒人負責全局導航 | agent 不知道該用哪個 skill | 在父層建立路由表，標示適用場景與排除條件 |
| **Context 過大**：單一 SKILL.md 超過 300 行 | 佔用過多 context window，降低推理品質 | 拆分多層架構，或將參考資料移到 `examples/` 按需載入 |

## 提交前檢查清單

| 類別 | 檢查項目 |
|------|----------|
| **目的** | 能用一句話說清楚這個 skill 解決的核心問題？ |
| **比例** | 原則/陷阱 vs 程式碼接近 80/20？沒有完整函數實作？ |
| **重複** | 沒有跟其他 skill 重複定義相同概念？ |
| **路由** | Agent 能從 description 快速判斷該不該用這個 skill？ |
| **精簡** | 行數 < 150？沒有 agent 能自行推斷的冗餘內容？ |
| **適用性** | 有情境限制的規則是否標記了適用範圍？ |
| **理由** | 每條「禁止/必須」規則是否附帶「為什麼」？ |
| **範例對齊** | `examples/` 中的程式碼是否遵守 SKILL.md 的規範？（吃自己的狗食） |
