# python-skills

跨 Agent 使用的 AI Skills 統一管理專案。

**Single Source of Truth** — 在這裡修改 skill，所有 AI 工具自動同步。

---

## 安裝與解除安裝

### 0. 取得專案

```bash
git clone https://github.com/your-org/python-skills.git
cd python-skills
```

> 建議 clone 到固定位置（如 `~/python-skills`），因為 install 腳本會建立 symlink 指向此目錄。移動或刪除源目錄會導致所有 AI 工具的 skill 失效。

腳本支援兩個維度的設定：**指定技能分類 (`--skills`)** 以及 **指定 AI 工具**。

### 1. 指定技能分類 (可選)
為了避免不相關的技能污染 AI 的上下文，你可以透過 `--skills` 參數來指定要安裝或移除的技能分類（支援前綴比對）。如果沒有加上此參數，則預設安裝/移除**所有**技能。

```bash
# 只安裝 Python 相關與 Git 相關的技能
bash install.sh --skills "python,git"

# 安裝所有的量化技能與通用 Python 技能
bash install.sh --skills "quant,python"
```

### 2. 指定 AI 工具 (可選)
你可以把 AI 工具名稱標註在指令後方。如果不加上任何工具名稱，腳本會**自動尋找**系統中已經存在的 AI 工具資料夾（如 `~/.cursor`）並全部安裝。

```bash
# 明確指定只安裝到 cursor 和 gemini
bash install.sh cursor gemini

# 結合上述兩者：只將 python 和 git 技能安裝到 cursor
bash install.sh --skills "python,git" cursor
```

支援的 AI 工具參數名稱包含：`antigravity`, `claude`, `codex`, `cursor`, `gemini`, `copilot`, `opencode`, `windsurf`。

> ⚠️ 解除安裝 (`bash uninstall.sh`) 的用法與上述完全一致，也支援 `--skills` 分類解除以及指定 AI 工具。

---

## 目錄結構

我們採用依賴關注點分離（Separation of Concerns）的設計，將技能歸類至不同的目錄：

```
python-skills/
├── skills/                           
│   ├── git/                          # 版本控制與協作 (如 conventional-commits)
│   ├── python/                       # 程式語言規範 (如 coding-standards)
│   ├── quant/                        # 特定業務領域邏輯 (如回測、資料預處理)
│   ├── skill-creator/                # 產生技能的 Meta-tool
│   └── (其他分類...)                 
│       ├── [技能名稱]/
│       │   ├── SKILL.md              # 主文件（必要存在，AI 載入點）
│       │   └── (其他關聯參考文件)
├── install.sh                        # 安裝腳本（建立 symlink）
├── uninstall.sh                      # 移除腳本（清除 symlink 與空資料夾）
└── README.md
```

---

## 支援的 AI 工具

| 工具 | 本地路徑 | 全域路徑 |
|------|----------|----------|
| Antigravity | `.agent/skills/` | `~/.gemini/antigravity/skills/` |
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |
| Codex | `.agents/skills/` | `~/.agents/skills/` |
| Cursor | `.cursor/skills/` | `~/.cursor/skills/` |
| Gemini CLI | `.gemini/skills/` | `~/.gemini/skills/` |
| GitHub Copilot | `.github/skills/` | `~/.copilot/skills/` |
| OpenCode | `.opencode/skills/` | `~/.config/opencode/skills/` |
| Windsurf | `.windsurf/skills/` | `~/.codeium/windsurf/skills/` |

> 參照 [awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills)
> 如需新增工具或修正安裝路徑，請編輯 [`_config.sh`](./_config.sh)，install / uninstall 腳本會自動套用。

---

## Quant Skills 概覽

量化分析技能集以 pipeline 架構組織，詳見 [入口 SKILL.md](./skills/quant/SKILL.md) 的完整路由表。


| Skill | 定位 |
|-------|------|
| [coding-standards](./skills/quant/coding-standards/SKILL.md) | 跨層通用規範：前視偏誤、IS/OOS 切分、數值穩定性 |
| [data-preprocessing](./skills/quant/data-preprocessing/SKILL.md) | 資料清洗、缺失值、去極值、標準化、跨頻率對齊 |
| [strategy-construction](./skills/quant/strategy-construction/SKILL.md) | 通用策略設計原則 + 截面選股的信號組合與權重分配 |
| [risk-management](./skills/quant/risk-management/SKILL.md) | VaR/CVaR、曝險控制、槓桿、回撤保護、壓力測試 |
| [execution-simulation](./skills/quant/execution-simulation/SKILL.md) | 滑價、漲跌停、市場衝擊、做空成本、結算 |
| [performance-evaluation](./skills/quant/performance-evaluation/SKILL.md) | Sharpe/MDD/Sortino 陷阱、因子評價、換手率分析 |
| [multiple-testing](./skills/quant/multiple-testing/SKILL.md) | FDR 校正、Haircut Sharpe、Placebo Test、實驗日誌 |
| [regime-analysis](./skills/quant/regime-analysis/SKILL.md) | Regime 分類、結構性斷裂偵測、循環論證防護 |

---

## 新增 Skill 的 SOP

1. 在 `skills/` 下的對應分類中建立新目錄（如 `skills/python/new-skill/`）
2. 建立 `SKILL.md`，必須包含 YAML frontmatter：
   ```yaml
   ---
   name: skill-name
   description: 一段清楚的描述，說明 AI 在什麼情境應該啟用這個 skill
   ---
   ```
3. 執行 `bash install.sh` 更新 symlink
4. 開始一個新對話測試 AI 是否正確載入 skill

---

## 更新技巧

修改任何 `SKILL.md` 後，**不需要重新執行 `install.sh`**——symlink 指向的是目錄，源文件更新後所有 Agent 裡的設定會即時生效。

只有在**新增或刪除 skill 目錄**時才需要重新執行 `install.sh`。

---

## 解除安裝

```bash
# 全部解除安裝
bash uninstall.sh

# 只解除指定分類的安裝
bash uninstall.sh --skills "quant"
```

只會移除 symlink，不會動到本專案的任何源文件。
