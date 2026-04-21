---
name: ito-browser-verify
description: 使用連接瀏覽器的工具，依據驗收標準或 PRD 執行 UI 層整合驗證，產出結構化報告並存至 local。使用者要求「做 UI 驗證」、「驗收 PRD 或 issue」、「用瀏覽器驗剛完成的功能」時使用。不適用於純 API 或後端驗證，亦不適用於需要自動修復 bug 的情境。
---

# ito-browser-verify

## 概覽

依據使用者提供的驗收標準或 PRD，藉由連接瀏覽器的工具執行 UI 層整合驗證。此 skill 為獨立工具，不綁定既有 ito pipeline，僅負責「執行驗證並產出事實報告」，修復工作交由其他 skill 處理。驗證前強制完成 Planning 並取得使用者批准，結果以結構化 markdown 存至本地 `docs/verify/`。

## 使用時機

- 使用者要求「做 UI 整合驗證」、「驗收 PRD 或 issue」、「用瀏覽器驗剛完成的功能」。
- 使用者提供驗收標準（透過 GitHub issue URL、本地 markdown 檔，或對話中貼入）並希望透過瀏覽器操作確認功能是否符合預期。
- 需要產出結構化驗證報告供事後追溯，或作為後續 `ito-tdd` Prove-it 變體的 reproduction 來源。

**不應使用的情況：** 純 API 或後端驗證（應改由呼叫端或 integration test 處理）、需要自動修復 bug 的情境（應使用 `ito-tdd` 的 Prove-it 變體）、單純探索或閱讀程式碼的任務。

## 核心流程

### 步驟 1：偵測瀏覽器工具可用性

1. **確認 sandbox 狀態**：agent 無法可靠自我偵測 Claude Code sandbox，直接詢問使用者「目前 Claude Code 是否在 sandbox 模式執行？」並以使用者回覆為準，不從環境變數或試探性指令自行推論。
2. **若 sandbox 為開啟**：明確告知使用者 `/playwriter` 需要存取本機 Chrome 與 Playwriter extension，sandbox 會阻擋相關呼叫；請使用者關閉 sandbox 後回覆確認。未收到明確確認前，不得進入後續任何步驟，也不得預先呼叫任何瀏覽器工具。
3. **檢查 `/playwriter` 可用性**：自當前對話前文的 available skills 清單（由 Claude Code 以 system-reminder 提供）中查找名為 `playwriter` 的 skill。
4. **若 `/playwriter` 存在**：將其記錄為本次驗證唯一使用的工具，進入步驟 2。後續步驟一律透過 Skill tool 呼叫 `/playwriter`，不自行呼叫底層 CLI 或繞過 skill 直接操作瀏覽器。
5. **若 `/playwriter` 不存在**：向使用者說明該 skill 未載入，請其指定替代工具（例如 Playwright MCP、Chrome DevTools MCP）。取得回覆後將所選工具記錄為本次驗證工具。
6. 整個流程以此步驟確立的工具作為唯一的瀏覽器操作來源，不得混用。

### 步驟 2：解析驗收標準來源

1. 讀取 `references/input-resolution.md` 以擷取三種輸入型態的判別規則與擷取流程。
2. 依擷取流程辨識輸入型態，並取得原始文本。
3. 自原始文本中抽取驗收標準條目，編號為 AC-1、AC-2、…。

### 步驟 3：分類與 Planning

1. 讀取 `references/non-ui-classification.md` 以提取 UI 可驗證與非 UI 項目的判別原則。
2. 將每條 AC 分類為「UI 可驗證」或「非 UI（跳過）」，非 UI 者須標註跳過原因（例如「屬於後端 API 契約」、「需資料庫檢查」）。
3. 針對每條 UI 可驗證的 AC，產出 step-by-step 的操作 plan：
   - 起始 URL 與前置狀態假設。
   - 操作序列（每步以「動作 + 目標元素」描述）。
   - 預期觀察結果（以可觀察的 UI 狀態描述，不描寫內部實作）。
4. 彙整本次驗證的 prerequisites 清單：dev server 是否已啟動並監聽目標 URL、使用者是否已登入對應帳號、test data 是否已 seed、瀏覽器是否處於預期初始分頁。
5. 將分類結果、逐條 plan、prerequisites 清單輸出給使用者，並**明確暫停等待批准**。

### 步驟 4：等待使用者批准與 prerequisites 確認

1. 在使用者回覆「OK」或等義確認之前，不得呼叫任何瀏覽器操作。
2. 若使用者針對分類或 plan 提出修改意見，回到步驟 3 相應子項調整後重新送審。
3. 若使用者表示 prerequisites 尚未就緒，停止流程並等待使用者完成準備後再行確認，不代為啟動 dev server、登入或 seed data。

### 步驟 5：逐條執行驗證

1. 依 plan 中的 AC 順序逐條執行，每條 AC 獨立記錄結果。
2. 對每條 AC：
   - 依 plan 操作序列呼叫步驟 1 所選的瀏覽器工具。
   - 比對實際 UI 狀態與預期觀察結果。
   - 若符合預期，標記為 ✅ Pass；若不符合，標記為 ❌ Fail，並進入 Evidence 收集。
3. **Evidence 收集**：當一條 AC 判定為 Fail，讀取 `references/evidence-checklist.md` 以提取必收欄位清單，逐項收齊後再進入下一條 AC。
4. 一條 AC 失敗不影響後續 AC 執行；除非使用者明確要求中止，否則 plan 中的所有 UI AC 都必須跑完。
5. 非 UI AC 在此步驟不執行任何瀏覽器操作，直接標記為 ⏭️ Skipped 並保留步驟 3 記錄的跳過原因。

### 步驟 6：產出本地報告

1. 讀取 `assets/report-template.md` 以提取報告骨架。
2. 執行 `scripts/make-slug.sh <topic>`，以驗證目標名稱（PRD 主題或 issue slug）產生檔名 `[slug]-[timestamp].md`。
3. 依骨架填入 Summary、每條 AC 的狀態與細節、以及所有 Fail 項的 TDD Prove-it Reproduction Spec。
4. 寫入 `docs/verify/[slug]-[timestamp].md`；若 `docs/verify/` 目錄不存在，先建立目錄。
5. 向使用者回報檔案路徑、Pass／Fail／Skipped 統計，不輸出整體通過判定（由使用者自行裁量）。

## 具體技巧／模式

### 報告骨架要點

報告為人類可讀的驗證紀錄，Fail 項同時承載 `ito-tdd` Prove-it 變體可直接取用的 reproduction spec。因此：

- 每條 Fail 的 AC 必附「失敗操作序列」、「failure signature」、「URL／user／state context」與「相關 API response 或 DOM 節點」四項，缺一不可。
- Evidence（Screenshot、Console、DOM、Network、Actual vs Expected）僅作為 Fail 判定的佐證與 reproduction spec 的擷取來源，不入報告主文。
- Skipped 項必列出跳過原因，避免日後回顧無法分辨是遺漏還是刻意略過。

### Planning 翻譯原則

將 AC 翻譯為操作序列時：

- 優先以使用者可觀察的語彙描述（「看見登入按鈕」而非「DOM 出現 `.login-btn`」）。
- 僅在必要時才於括號中補充 selector 提示。
- 預期結果描述以「狀態變化」為主（「頁面導向 /dashboard 且顯示使用者名稱」），而非單一元素存在與否。

## 常見合理化藉口

| 合理化藉口 | 實際情況 |
|---|---|
| 「sandbox 狀態可從環境變數自行推測，不必問使用者」 | agent 無法可靠查詢 Claude Code 的 sandbox 旗標；猜錯會讓 `/playwriter` 在執行中途被阻擋，白費前面 planning。 |
| 「available skills 清單沒列 `playwriter`，但 CLI 有裝，直接呼叫 CLI 就好」 | 本流程以 skill 為主要介面；繞過 skill 直接呼叫 CLI 會跳過 skill 的狀態管理與 evidence 介接格式，Fail 欄位後續無法套用。 |
| 「plan 很簡單，直接開跑比較快」 | 跳過批准會導致 URL、test account 等歧義在執行中才暴露，整個流程必須重跑，反而更慢。 |
| 「dev server 沒啟動，我先幫使用者跑 `npm run dev`」 | 此 skill 明確將環境準備責任劃給使用者；代為啟動會踩到 port 衝突、monorepo 多 app 的誤判風險。 |
| 「這條 AC 看起來是 API 類，但順便也驗一下」 | 非 UI AC 在瀏覽器層只能間接觀察，驗了也無法分辨是 UI 問題還是後端問題，應維持 Skipped 分類。 |
| 「Fail 已截圖，其他 evidence 省略」 | 缺少 console、DOM、network 等欄位，下游 `ito-tdd` Prove-it 無法重現問題，報告價值大幅降低。 |
| 「使用者說驗完趕快給結論，我補一個整體 PASS／FAIL」 | 通過判定屬於使用者裁量範圍；擅自下整體結論違反「純回報」的職責邊界。 |

## 警訊

- 未向使用者確認 sandbox 狀態就開始呼叫瀏覽器工具。
- sandbox 仍為開啟時繼續嘗試呼叫 `/playwriter` 或替代工具。
- available skills 清單中沒有 `playwriter`，卻仍以 `/playwriter` 呼叫而非 fallback。
- Planning 尚未取得批准就開始呼叫瀏覽器工具。
- Plan 中出現未列於 prerequisites 的環境假設（例如隱含「使用者已登入」卻未在清單中列出）。
- 非 UI AC 被收入 UI 驗證序列而未標註跳過。
- Fail 項的 Evidence 欄位不齊，或缺少 TDD Prove-it Reproduction Spec。
- 報告出現整體 PASS／FAIL 結論。
- 一條 AC 失敗後，其餘 AC 遭到中止而未事先取得使用者同意。

## 驗證

- [ ] 步驟 1 已向使用者確認 sandbox 狀態；若曾為開啟，已取得使用者關閉後的明確回覆再繼續。
- [ ] 步驟 1 已從 available skills 清單驗證 `/playwriter` 是否存在；不存在時已取得使用者指定的替代工具。
- [ ] 步驟 1 已確立本次使用的瀏覽器工具，且在整個流程中未被替換。
- [ ] Planning 已輸出分類結果、逐條 plan、prerequisites 清單，且已取得使用者明確批准。
- [ ] 所有 UI 可驗證 AC 皆留下 Pass 或 Fail 結果，Fail 項 Evidence 欄位齊備。
- [ ] 非 UI AC 皆標記為 Skipped 並附跳過原因。
- [ ] 報告已寫入 `docs/verify/[slug]-[timestamp].md`，檔名透過 `scripts/make-slug.sh` 產生。
- [ ] 報告未出現整體通過判定。

## 錯誤處理

- 若使用者對 sandbox 狀態不確定，停止流程並請使用者於 Claude Code 側自行確認後回覆；回覆取得前不得進入步驟 2。
- 若 `/playwriter` 雖在 skill 清單中但呼叫時回報 extension 未連線或 CLI 缺失，將情況回報使用者並請其指定替代工具，不自行繞過 skill 直接呼叫 CLI。
- 若 `gh issue view` 回傳非 0 或內容為空，向使用者確認 issue URL 是否正確，或改請使用者直接貼入驗收標準。
- 若輸入內容無法抽出任何驗收標準，停止流程並向使用者說明「輸入中未偵測到可驗證項目」，不進入 Planning。
- 若驗證中途使用者撤回 prerequisites（例如 dev server 中斷），停止執行並保留當下已完成 AC 的結果，詢問使用者是否恢復後續流程或直接依目前進度產報告。
- 若 `docs/verify/` 目錄所在專案並非 git repo，仍正常寫入檔案；僅將此情況於回報訊息中提醒使用者。

## 延伸參考

- `/playwriter`：本 skill 優先使用的瀏覽器控制 skill，透過 Playwriter extension 操控使用者本機 Chrome。
- `ito-tdd`：修復階段使用。此 skill 產出的 TDD Prove-it Reproduction Spec 可直接作為 `ito-tdd` Prove-it 變體的 failing test 起始點。
- `ito-grill`：當驗收標準本身語意不明，或需要先釐清驗證策略時，由使用者主動切換使用。
- `references/input-resolution.md`：三種輸入型態的解析規則。
- `references/non-ui-classification.md`：UI 與非 UI 項目的分類原則。
- `references/evidence-checklist.md`：Fail 項 Evidence 必收欄位清單。
- `assets/report-template.md`：本地報告 markdown 骨架。
