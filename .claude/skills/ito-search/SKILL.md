---
name: ito-search
description: 處理所有外部查詢需求，包含套件用法與 API、錯誤訊息、GitHub issue/PR、方法論與一般知識，必要時對比 codebase 現況。以「幫忙查」、「搜尋一下」等自然語觸發，或明確呼叫 `/ito-search`。不適用於需直接實作、修改檔案、跑測試的任務，或需存檔的調研任務。
---

# ito-search

## 概覽

提供多種外部搜尋工具，由 agent 依查詢內容自行挑選合適工具（單用、並用或平行）。結果經劣質網域黑名單過濾後，依輸出原則回覆。整個流程為一次性查詢，不存檔。

## 使用時機

- 使用者明確呼叫 `/ito-search`
- 使用者以自然語觸發外部資訊查詢：「幫我查⋯」「搜尋一下⋯」「找一下⋯」「XXX 怎麼用」「XXX 是什麼」
- 在 git repo 下查詢 best practice / pattern / architecture / 套件用法（自動偵測並詢問是否對比 codebase 現況）

**不應使用的情況：** 需要直接實作、修改檔案、跑測試的任務，需產出研究報告或需存檔的調研任務。

## 核心流程

### 步驟 0：codebase 掃描 偵測與確認

若查詢類型為 best practice / pattern / architecture / 套件用法，**且**當前工作目錄在 git repo 下，詢問使用者：

> 偵測到此查詢可能需要對比 codebase 現況。要先掃描相關檔案再搜尋嗎？

- **使用者同意**：序列執行以下流程：
  1. 掃描 codebase：agent 依查詢主題自由判斷掃哪些相關檔案（不限白名單）
  2. 帶著 codebase 現況執行步驟 1 外部搜尋
  3. 產出缺口分析（對比 codebase 現況與社群建議）
  4. **強制驗證**：每條缺口輸出前，必須對該項目做 `grep`/`read` 確認。未經驗證不得輸出。
  5. 進入步驟 2 過濾與步驟 3 輸出
- **使用者拒絕**：跳過掃描，直接進入步驟 1 原有流程

其他查詢類型（API 語法、錯誤訊息、一般知識等）跳過步驟 0，直接進入步驟 1。

### 步驟 1：依查詢內容自選工具

從下列工具清單擇一或擇數使用，查詢內容明確橫跨兩個以上工具分類時平行執行對應工具，否則序列執行。執行至各工具回傳結果為止。

#### 找官方文件（/find-docs skill，context7 MCP Fallback）

- 用途：查 lib/framework/SDK/CLI 的官方 API、syntax、code snippet、設定與版本特定資訊
- 區分訊號：查詢內容含具體 lib 名稱與「怎麼用」「API」「語法」「snippet」「設定」等實作詞
- 執行順序：
  1. 呼叫 `/find-docs` skill 執行查詢
  2. `/find-docs` 失敗（任何原因，包含配額 / 認證失敗）時，忽略 find-docs 的錯誤處理邏輯，改用 context7 MCP 執行相同查詢

#### deepwiki（MCP）

- 用途：查 GitHub repo 內部運作、架構問答、為何如此設計
- 區分訊號：查詢內容含具體 GitHub `owner/repo` 與「怎麼運作」「為什麼這樣設計」「架構」等問答詞，非 SDK/lib 名稱（後者改用工具 A）

#### exa（MCP）

- 用途：bug 訊息/社群討論、best practice/方法論/架構、非技術一般知識
- 區分訊號：查詢內容為錯誤訊息、抽象方法論詞（best practice/pattern/architecture）、或非技術問題
- 時效偏好：呼叫前於查詢字串附加近一年時間提示，降低命中過舊資料機率。查詢內容已含具體版本、年份或本身為歷史主題時，agent 自行判斷略過此提示。純偏好，不對結果做硬過濾

#### gh（CLI）

- 用途：追蹤 GitHub issue/PR/release/action、社群討論
- 區分訊號：查詢內容含 repo 名與 issue/PR 編號或具體 issue 關鍵字

#### Fallback：harness 內建搜尋工具

上述所有工具失敗或回傳零結果時，靜默改用 harness 內建 `WebSearch`/`WebFetch`，不告知使用者工具切換。

### 步驟 2：過濾結果

讀取 `references/source-filter.md` 以取得黑名單清單，對所有結果 URL 做 substring match，命中黑名單者整筆剔除。

### 步驟 3：依輸出原則回覆

格式由 agent 依查詢性質自決：

- **簡單查詢**（一句話可答）：直接回答，末段附「來源」區塊，列出可點擊 URL 清單
- **複雜/資訊豐富查詢**：TL;DR 段（一至三句核心摘要）、說明段（展開細節，可含 code block）、末段「來源」區塊

## 常見合理化藉口

| 合理化藉口 | 實際情況 |
|---|---|
| 「/find-docs 失敗，直接跳 exa 搜就好」 | /find-docs 失敗要先 Fallback 到 context7 MCP，不是跳過工具 A 整個分支 |
| 「查詢很短，跳過工具選擇直接 exa 搜就好」 | 短查詢可能是 API 語法問題，跳過工具選擇讓文件命中率大幅下降 |
| 「結果過濾後沒幾筆，補幾筆黑名單域名的結果」 | 過濾後結果少時應 Fallback 至 WebSearch，不放行黑名單域名 |
| 「使用者沒說要附來源，可省略來源區塊」 | 來源區塊是輸出契約，供使用者驗證，不可省略 |
| 「codebase 掃完、外部搜尋也做了，直接輸出缺口」 | 每條缺口輸出前必須對該項目做 grep/read 驗證，未驗證的推斷不得輸出 |

## 警訊

- 輸出缺少「來源」區塊
- 結果含黑名單域名（如 `csdn.net`、`w3schools.com`）未過濾
- `/find-docs` 失敗後未嘗試 context7 MCP 直接跳至下一工具
- 複雜查詢無摘要直接展開大段說明
- 呼叫 exa 時未加時效提示，且查詢內容非歷史主題或未指定版本
- 缺口未對每條做 grep/read 驗證即輸出

## 驗證

- [ ] 結果經 `references/source-filter.md` 黑名單過濾，輸出無命中域名
- [ ] 輸出含「來源」區塊與可點擊 URL 清單
- [ ] 未建立任何檔案（不存檔）
- [ ] `/find-docs` 失敗時已嘗試 context7 MCP Fallback
- [ ] codebase 掃描模式：每條缺口均有 grep/read 驗證，未驗證項目已標記「未能驗證」

## 錯誤處理

- **工具 A 失敗**（/find-docs 配額 / 認證失敗或任何錯誤）：忽略 find-docs 錯誤邏輯，靜默改用 context7 MCP
- **其他工具失敗**（配額 / 認證失敗 / 零結果）：fallback 至下一個合理工具
- **所有工具失敗**：靜默改用 harness 內建 `WebSearch`/`WebFetch`，不中斷回覆
- **codebase 掃描後缺口驗證失敗**（grep/read 找不到對應符號）：標記「未能驗證」並說明原因，不直接斷言缺失

## 延伸參考

- `references/source-filter.md`：劣質網域黑名單清單
- `/find-docs` skill：ctx7 CLI 的兩步驟用法（library → docs）
- `context7` MCP：`/find-docs` CLI 失敗時的Fallback，提供相同文件查詢能力
- `exa` MCP：網路搜尋、網頁爬取與深度研究
- `deepwiki` MCP：GitHub repo AI 生成文件，可直接問答架構與設計
- `gh` CLI：GitHub issue/PR/release/action 查詢與追蹤
