# Local NER MCP Server

Local NER MCP Server 是供本機 Codex 使用的外掛。Skill 把來源檔案整理成一份具名的標註參考 JSON。唯讀 MCP Server 提供詞表清單與原文比對。

[英文 README](README.md) · [繁體中文 HTML](README_zh-TW.html)

## 安裝方式

準備 Codex CLI 和可執行 `python3` 的 Python 3.10 以上環境。MCP Server 首次啟動時會下載 Python 依賴，並在使用者目錄建立可重用的執行環境。

### 從 GitHub 安裝

有權讀取 `cclintw/textoria-ner-mcp-server` 儲存庫時，在終端機執行以下指令，即可下載外掛目錄並安裝 Skill 和 MCP Server。

```sh
codex plugin marketplace add cclintw/textoria-ner-mcp-server && codex plugin add local-ner-mcp-server@local-ner
```

### 從本機安裝

已有專案檔案時，可在儲存庫根目錄執行以下指令。

```sh
codex plugin marketplace add . && codex plugin add local-ner-mcp-server@local-ner
```

也可在桌面 App 開啟本專案，從**外掛程式 → 瀏覽目錄 → Local NER**選擇並安裝 **Local NER MCP Server**。

## 建立標註參考表

1. 開啟新的本機 Codex 對話，上傳 CSV、TSV、JSON、GeoJSON 或 SQLite 等來源檔。
2. 在輸入框用 `$` 選擇 **Local NER MCP Server**，也可輸入 `$local-ner-mcp-server:local-ner-mcp-server`。指定詞表名稱，例如「將這份檔案整理成『台灣地名』標註參考表」。
3. 開啟產出的 JSON。Skill 會判讀來源欄位，驗證抽取的實體與關係，並說明無法對應的記錄。

每份詞表預設存於 `~/.codex/local-ner-mcp-server/reference_sets/`，檔名使用詞表 ID。新增詞表後，可以沿用同一個 MCP Server 查詢。欄位定義見[參照表格式](plugins/local-ner-mcp-server/skills/local-ner-mcp-server/references/reference-format.md)。

## 調用 MCP 工具

| 工具 | 用途 |
| --- | --- |
| `list_reference_sets` | 列出可用詞表的 ID 與顯示名稱。 |
| `match_mentions` | 傳入詞表 ID `reference_set_id` 與原文 `text`，回傳精確命中的文字位置、候選實體、可用座標與相關關係。 |

比對保留重疊命中及同名候選。文字位置按 Unicode 字元計算，從 0 開始，終點為命中後的第一個位置。別名比對預設開啟，可在詞表的 `match_aliases` 規則調整。

在桌面 App 的**外掛程式 → MCP → 來自外掛程式**可查看伺服器。

## 首次啟動

若首次啟動因下載依賴逾時，可在本機儲存庫根目錄執行以下指令，再開啟新的本機 Codex 對話。

```sh
python3 -B plugins/local-ner-mcp-server/skills/local-ner-mcp-server/scripts/launch.py --setup
```

本機詞表可保存在預設的詞表目錄。專案的 Git 忽略規則涵蓋 `reference_sets/` 和既有本機詞表的檔名。
