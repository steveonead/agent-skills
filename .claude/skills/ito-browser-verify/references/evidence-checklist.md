# Fail 項 Evidence 必收欄位清單

本檔供 `ito-browser-verify` 主流程於步驟 5 擷取「一條 AC 判定為 Fail 時，必須收齊的 Evidence 欄位」，作為資料參照，非執行指令。

Evidence 作為 Fail 判定的佐證與 `ito-tdd` Prove-it 變體 reproduction spec 的擷取來源，僅於蒐集階段留存，不進入報告主文。因此每一欄位都不得省略。

## 必收欄位一覽

### 1. Screenshot

- 範圍：失敗判定當下的可見畫面，須包含失敗相關元素的上下文。
- 格式：以工具支援的截圖功能取得；於報告中以 markdown 嵌入圖片或描述檔案路徑。
- 目的：呈現失敗現場的視覺狀態。

### 2. Console Logs

- 範圍：失敗操作發生前後 30 秒內的 browser console 輸出，包含 `log`、`warn`、`error` 等所有層級。
- 格式：完整時間戳與訊息內容，不截斷。
- 目的：定位 runtime exception、deprecation warning、與前端邏輯的輸出軌跡。

### 3. DOM Snapshot

- 範圍：失敗判定當下，失敗元素及其最近上層容器的 HTML 結構。
- 格式：包含 tag、屬性、className、data-*、以及可複製的 CSS selector 或 XPath。
- 目的：供 `ito-tdd` 撰寫 failing test 時直接對應到元素。

### 4. Network Errors

- 範圍：失敗操作發生前後 30 秒內，status code ≥ 400 或 timeout 的所有 request／response。
- 格式：method、URL、status、request payload 摘要、response body 摘要。
- 目的：分辨 UI 問題是由前端狀態引起，抑或由後端錯誤傳導而來。

### 5. Actual vs Expected

- 範圍：Plan 中記錄的預期觀察結果，對比實際發生的 UI 狀態。
- 格式：兩欄並列，逐項比對差異。
- 目的：讓讀者無須重新推理即能理解失敗本質。

## TDD Prove-it Reproduction Spec 補充欄位

於上述五欄之外，每條 Fail AC 必附下列 reproduction spec，供 `ito-tdd` Prove-it 變體直接取用：

### 6. 失敗操作序列

- 範圍：從頁面初始狀態到失敗判定之間的完整操作步驟。
- 格式：編號清單，每步描述「動作 + 目標元素 + 輸入值」。
- 目的：作為 failing test 的 arrange／act 階段藍本。

### 7. Failure Signature

- 範圍：一句話描述失敗的本質（例如「預期 /dashboard 但實際 /login」、「預期成功 toast 但出現 error toast」）。
- 格式：自然語言單句，避免內部術語。
- 目的：作為 failing test 的 assertion 階段藍本與測試命名依據。

### 8. URL／User／State Context

- 範圍：失敗判定當下的 URL、登入使用者識別（email 或 user id，避免洩漏密碼）、以及相關的 app 狀態（例如購物車已有 N 項、目前為 step 2）。
- 格式：key-value 清單。
- 目的：供 `ito-tdd` 建立等價的測試環境。

### 9. 相關 API Response 或 DOM 節點

- 範圍：對理解失敗直接相關的 response payload 內容，或特定 DOM 節點的屬性值。
- 格式：JSON 片段或屬性清單，僅保留與失敗相關的欄位，避免過量傾倒。
- 目的：提供最小可重現資料。

## 欄位缺漏判定

若任一必收欄位在工具能力限制下無法取得（例如 `Console Logs` 因工具未提供 console 讀取而無法收集），於該欄位之蒐集紀錄中以下列字樣標註：

```
工具未支援 — 原本應為 <欄位用途>。
```

並將此限制於報告 Summary 區段提醒使用者，以便評估是否切換至其他工具再次驗證。
