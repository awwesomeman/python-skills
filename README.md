# quant-skills

跨 Agent 使用的 AI Skills 統一管理專案。

**Single Source of Truth** — 在這裡修改 skill，所有 AI 工具自動同步。

---

## 安裝與解除安裝

腳本支援**自動偵測**與**指定安裝**兩種模式：

### 自動偵測模式（推薦）
不加任何參數執行，腳本會自動尋找系統中已經存在的 AI 工具配置資料夾（例如 `~/.gemini` 或 `~/.cursor`），並只在有安裝的工具上建立 symlink：
```bash
git clone <this-repo> ~/path/to/quant-skills
cd quant-skills
bash install.sh
```

### 指定安裝模式
如果你只想安裝到特定的 AI 工具，可以在指令後方加上工具名稱（不分大小寫）：
```bash
bash install.sh cursor gemini
```

支援的參數名稱包含：`antigravity`, `claude`, `codex`, `cursor`, `gemini`, `copilot`, `opencode`, `windsurf`。

> ⚠️ 解除安裝 (`bash uninstall.sh`) 也支援上述同樣的**自動偵測**或**指定解除**參數。

## 目錄結構

```
quant-skills/
├── skills/                           # 將你的 AI skills 放這裡
│   ├── [skill-category]/             # 建立分類群組或單一 skill
│   │   ├── SKILL.md                  # 主文件（必要存在，AI 載入點）
│   │   └── (其他關聯參考文件)
│   └── (其他 skills...)
├── install.sh                        # 安裝腳本（自動掃描並建立 symlink）
├── uninstall.sh                      # 移除 symlink
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

---

## 新增 Skill 的 SOP

1. 在 `skills/` 下建立新目錄（如 `skills/strategy-dev/`）
2. 建立 `SKILL.md`，必須包含 YAML frontmatter：
   ```yaml
   ---
   name: skill-name
   description: 一段清楚的描述，說明 AI 在什麼情境應該啟用這個 skill
   ---
   ```
3. 執行 `bash install.sh` 更新 symlink（腳本會自動掃描所有含 `SKILL.md` 的目錄，無需修改腳本）
4. 開始一個新對話測試 AI 是否正確載入 skill

---

## 更新技巧

修改任何 `SKILL.md` 後，**不需要重新執行 `install.sh`**——symlink 指向的是目錄，目錄內的文件更新即時生效。

只有在**新增或刪除 skill 目錄**時才需要重新執行 `install.sh`。

---

## 解除安裝

```bash
bash uninstall.sh
```

只會移除 symlink，不會動到本專案的任何源文件。
