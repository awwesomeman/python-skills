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

```
Usage: bash install.sh [OPTIONS] [AI_TOOLS...]
```

| 參數 | 縮寫 | 說明 | 預設 |
|------|------|------|------|
| `--skills <list>` | `-s` | 指定要安裝的技能分類，逗號分隔，支援前綴比對 | 全部技能 |
| `--local` | `-l` | 將技能安裝到「執行這行指令所在的目錄」內（如專案根目錄下的 `.cursor/skills/` 等），而非全域安裝 | 全域路徑 |
| `--copy` | `-c` | 複製實際檔案取代 symlink，適用於無法保留 clone 的情境 | symlink |
| `[AI_TOOLS...]` | — | 指定目標 AI 工具（位置參數，可多個） | 自動偵測已安裝的工具 |

支援的 AI 工具名稱：`antigravity`, `claude`, `codex`, `cursor`, `gemini`, `copilot`, `opencode`, `windsurf`, `openclaw`。

### 範例

```bash
# 安裝所有技能到所有偵測到的 AI 工具（全域）
bash install.sh

# 只安裝 python 和 git 相關技能
bash install.sh --skills "python,git"

# 明確指定只安裝到 cursor 和 gemini
bash install.sh cursor gemini

# 組合：只將 python 和 git 技能安裝到 cursor
bash install.sh --skills "python,git" cursor

# 將技能安裝到「執行這行指令所在的目錄」內（如你的專案根目錄）
bash install.sh --local

# 完整組合：只將 python 技能安裝到 cursor 的本地路徑
bash install.sh --local --skills "python" cursor

# 複製模式：複製實際檔案而非建立 symlink
bash install.sh --copy cursor
```

> ⚠️ 解除安裝 (`bash uninstall.sh`) 的用法與上述完全一致，也支援 `--local`、`--skills` 分類解除以及指定 AI 工具。`uninstall.sh` 能自動辨識 symlink 與複製模式的安裝，使用相同指令即可解除兩種安裝。

### 遠端安裝（免 Clone）

不需要 clone 專案即可安裝，使用 `curl` 單行指令（自動使用 `--copy` 模式）：

```bash
# 安裝所有技能到所有偵測到的 AI 工具
curl -fsSL https://raw.githubusercontent.com/awwesomeman/python-skills/main/remote-install.sh | bash

# 只安裝 python 和 git 技能到 cursor
curl -fsSL https://raw.githubusercontent.com/awwesomeman/python-skills/main/remote-install.sh | bash -s -- --skills "python,git" cursor

# 將技能安裝到「執行這行指令所在的目錄」內（如你的專案根目錄）
curl -fsSL https://raw.githubusercontent.com/awwesomeman/python-skills/main/remote-install.sh | bash -s -- --local
```

> Fork 使用者可透過環境變數指定自己的 repo：`GITHUB_REPO=user/repo curl -fsSL <url> | bash`
>
> 遠端安裝自動使用 `--copy` 模式（複製檔案），因此更新技能內容後需重新執行安裝指令。

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
├── install.sh                        # 安裝腳本（symlink 或 copy）
├── uninstall.sh                      # 移除腳本（自動偵測 symlink 與 copy）
├── remote-install.sh                 # 遠端安裝腳本（免 clone，curl | bash）
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
| OpenClaw | `.openclaw/skills/` | `~/.openclaw/skills/` |

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

使用 **symlink 模式**（預設）修改任何 `SKILL.md` 後，**不需要重新執行 `install.sh`**——symlink 指向的是目錄，源文件更新後所有 Agent 裡的設定會即時生效。只有在**新增或刪除 skill 目錄**時才需要重新執行 `install.sh`。

使用 **`--copy` 模式或遠端安裝**的使用者，更新技能內容後需要**重新執行安裝指令**，因為檔案是獨立副本，不會自動同步。

---

## 解除安裝

```bash
# 全部解除安裝
bash uninstall.sh

# 只解除指定分類的安裝
bash uninstall.sh --skills "quant"

# 解除本地路徑的安裝
bash uninstall.sh --local
```

會自動辨識並移除 symlink 與複製模式的安裝，不會動到本專案的任何源文件。
