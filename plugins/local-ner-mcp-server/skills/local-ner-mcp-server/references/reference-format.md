# 參照表格式與匯入方式

## 來源欄位

| 格式 | 檢查項目 |
|---|---|
| CSV、TSV | 編碼、分隔符號、表頭與樣本列。依來源慣例判定別名分隔方式。 |
| JSON | 頂層結構、記錄陣列、巢狀欄位及跨記錄 ID。 |
| GeoJSON | 以 `properties` 取得名稱等屬性。標準 `Point` 依經度、緯度順序讀取。多邊形只有在來源提供可確認的代表點時才填入座標。 |
| SQLite | 唯讀開啟，檢查資料表、欄位、主鍵、外鍵及樣本。使用可確認的來源 ID 串接實體、異名和關係。 |

先抽樣判斷對應，再用可重複的程式轉換完整來源。可用原始 ID 作為實體 ID，來源沒有 ID 時以記錄產生唯一 ID。只有名稱的清單可採用 `unknown` 類型。同名記錄保留獨立。只有能指向既有實體的關係才寫入表中。可確認的經緯度統一為 WGS 84。座標缺漏、座標系統不明、無法連接的關係等列入審核摘要。

## JSON

頂層固定欄位為 `schema_version`、`id`、`name`、`entities`、`relations`、`rules`。目前版本為 `1`。參照表 ID 以小寫英數、連字號組成，可加短識別碼區分同名表。儲存位置為 `~/.codex/local-ner-mcp-server/reference_sets/<id>.json`。指令與 Server 都可使用 `--data-dir` 指定其他目錄。

| 項目 | 欄位 |
|---|---|
| 實體 | `id`、`name`、`type`、`aliases`。別名是字串陣列，沒有別名時用空陣列。地名類型為 `place`，其餘可用 `person`、`organization`、`unknown` 或來源適用的類型。 |
| 地名座標 | 在地名實體加上選填的 `location`，包含數值欄位 `longitude` 和 `latitude`。 |
| 關係 | `subject_id`、`type`、`object_id`。兩端使用同份參照表的實體 ID。沒有關係時，`relations` 為空陣列。 |
| 規則 | `rules` 是設定物件。目前支援布林值 `match_aliases`，預設為 `true`。使用預設值時可填入空物件。 |

比對採原文精確匹配，保留重疊命中。同一文字範圍的多筆候選合併回傳。位置以 Unicode 字元計算，起點從 0 開始，終點為命中後第一個字元的位置。
