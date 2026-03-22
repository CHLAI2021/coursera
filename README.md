Weather & Geolocation Map (結合天氣與喜好的個人化地圖)
透過 OpenWeather 與 Geocoding API，將純文字的地址轉換為帶有即時天氣資訊的互動式地圖。

關於本專案 (About The Project)
這是一個結合地理資訊與氣象數據的 Python 爬蟲與資料視覺化專案，作為完成密西根大學 PY4E (Python for Everybody) 課程後的技術延伸與自我驗收。
本專案跳脫給定的靜態測資，從資料庫讀取自定義的地點清單，透過 API 抓取經緯度與即時天氣，將兩方資料縫合後匯出成 JavaScript 格式，最終渲染於前端 HTML 網頁地圖上。

技術堆疊 (Built With)
後端邏輯： Python 3

資料庫： SQLite3 (處理關聯式資料與游標操作)

資料格式： JSON, Bytes (二進位存取)

前端渲染： JavaScript, HTML/CSS (地圖顯示)

外部 API： OpenWeather API, 課程提供之 Geocoding API

專案架構與資料流 (How It Works)
geoload.py： 讀取設定的地點清單，向 Geocoding API 請求經緯度資料，並以二進位 (BLOB) 格式存入 SQLite 資料庫。

weatherload.py： 讀取已查找到的地點，向 OpenWeather API 請求即時氣象資料，同樣存入 SQLite。

weatherdump.py (核心引擎)： 運用雙游標 (Dual Cursors) 同時讀取天氣與地理表格。以精確的天氣資料為基準去查找地點座標，將資料解碼縫合後，轉換為前端可讀的 where.js 陣列。

where.html： 讀取 where.js，在瀏覽器地圖上打點並顯示包含氣溫與時間的互動式氣泡。

開發挑戰與技術決策 (Challenges & Learnings)
挑戰 1：客製化需求引發的游標衝突 (Cursor Collision)
問題： 在讀寫資料庫的過程中，若同時進行 SELECT (讀取) 與 UPDATE/INSERT (寫入) 且共用同一個資料庫游標，會引發 sqlite3.InterfaceError 導致資料遺失或報錯。

解法： 引入雙游標機制 (Dual Cursors)。在程式碼中明確宣告並分離讀取與寫入的游標（例如 weather_cur 與 location_cur），徹底解決讀寫衝突，確保大資料量下的迴圈穩定運行。

挑戰 2：資料流反轉與二進位型態轉換 (Data Type Conversion)
問題： SQLite 在儲存 Geocoding 回傳的龐大 JSON 結構時採用二進位 (BLOB) 格式。在最終縫合資料時，必須處理 Python 字串與二進位之間的型態轉換。

解法： 為了確保地圖標記的準確性，我決定以「天氣資料」為 Base 進行迴圈（因為天氣資料更為精確乾淨）。拿著天氣地點去查詢座標時，先利用 .encode() 將字串轉為 Bytes 進入資料庫比對；抓出資料後，再利用 .decode() 轉回字串，最後透過 json.loads 成功解析。這段過程極大化了對資料型態底層運作的理解。

挑戰 3：API 限制與防禦性編程 (Defensive Programming)
問題： 真實世界的 API 狀態極不穩定，偶爾會回傳空值 (None)、缺少特定 Key，或是部分地點根本查無資料，導致程式輕易崩潰。

解法： 揚棄全包式的 Try-Except，改為實作**「精準分層」的多層 try...except 區塊**。針對 JSONDecodeError 與 KeyError 獨立攔截，並加入計數器 (not_found) 記錄失敗次數。這不僅防止了程式中斷，更自然形成了一道資料過濾器 (Data Filter)——讓有缺漏的髒資料安靜地被 continue 放棄，確保最終寫入 JS 檔的每一筆資料都是完美無缺的。

授權與致謝 (Acknowledgments)
基礎架構啟發自密西根大學 Dr. Chuck 的 Python for Everybody (PY4E) 課程。

特別感謝這段期間不眠不休與 Bug 奮戰的自己。