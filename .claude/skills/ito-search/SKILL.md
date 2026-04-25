---
name: ito-search
description: 提供 ctx7 cli／context7 mcp／deepwiki／exa／gh 等外部搜尋工具組，由 agent 依 query 自選工具並過濾劣質網域，輸出附來源 URL。以「幫我查」、「搜尋一下」等自然語觸發。不適用於 codebase 搜尋、需直接實作的任務、需長期保留結果的研究。
---

# ito-search

## 概覽

提供一組外部搜尋工具，由 agent 依使用者 query 自行挑選合適工具（單用、並用或同訊息多 tool call 平行）。結果經劣質網域黑名單過濾後，依輸出原則回覆。整個流程為一次性查詢，不存檔。

## 使用時機

- 使用者明確呼叫 `/ito-search`
- 使用者以自然語觸發外部資訊查詢：「幫我查⋯」「搜尋一下⋯」「找一下⋯」

**不應使用的情況：** 任何 codebase 搜尋；需要直接實作、修改檔案、跑測試的任務。

## 核心流程

### 步驟 1：依 query 自選工具

從下列工具清單擇一或擇數使用，根據需求判斷是否需要平行搜尋，執行至各工具回傳結果為止。無結果時走錯誤處理。

#### 工具 A：找官方文件（/find-docs skill）

- 用途：查 lib／framework／SDK／CLI 的官方 API、syntax、code snippet、設定與版本特定資訊
- 區分訊號：query 含具體 lib 名稱與「怎麼用」「API」「語法」「snippet」「設定」等實作詞

#### 工具 B：deepwiki（MCP）

- 用途：查 GitHub repo 內部運作、架構問答、為何如此設計，也可以作為 `/find-docs` 內容的補充
- 區分訊號：query 含具體 GitHub `owner/repo` + 「怎麼運作」「為什麼這樣設計」「架構」等問答詞；非 SDK／lib 名稱（後者改用 `/find-docs`）

#### 工具 C：exa（MCP）

- 用途：bug 訊息／社群討論、best practice／方法論／架構、非技術一般知識
- 區分訊號：query 為錯誤訊息、抽象方法論詞（best practice／pattern／architecture）、或非技術問題

#### 工具 D：gh（CLI）

- 用途：追蹤 GitHub issue／PR／release／action、社群討論
- 區分訊號：query 含 repo 名與 issue／PR 編號或具體議題關鍵字

#### Fallback：harness 內建搜尋工具

- 用途：上述工具全失敗時的最後手段，或 fetch 已知 URL

### 步驟 2：過濾結果

讀取 `references/source-filter.md` 以擷取黑名單清單。對所有結果 URL 做 substring match，命中黑名單者整筆剔除。過濾後若結果為空，跳至「錯誤處理」對應條目。

### 步驟 3：依輸出原則回覆

不指定範本，但必須符合下列原則：

- **附來源 URL**：每個引用點以 `[1]`、`[2]` 標註，並於末段「來源」列出對應可點擊 URL 清單，編號一一對應
- **附使用工具**：末段一行標明「使用工具：X」（單工具）或「使用工具：X、Y」（多工具）
- **主體格式自決**：依 query 性質選擇——API／文件類可內嵌 code block 或原文片段，討論／方法論類可摘要彙整，非技術類純文字皆可

## 常見合理化藉口

| 合理化藉口 | 實際情況 |
|---|---|
| 「query 很短，跳過工具選擇直接 exa 搜就好」 | 跳過工具選擇會讓 API／文件類 query 走通用 web 搜尋，文件命中率大幅下降；步驟 1 工具自選不可省 |
| 「結果經過濾後沒幾筆，補幾筆低質的湊數」 | 違反「品質過低不勉強回」原則；應走錯誤處理流程，告知使用者並給候選 query |
| 「使用者沒明說要附出處，可省略 URL」 | 強制附出處為 skill 核心契約，目的是供使用者驗證；省略違反設計目的 |

## 警訊

- 輸出缺少「來源」段或缺少末段「使用工具：X」
- 結果含黑名單域名（如 `csdn.net`、`51cto.com`、`tutorialspoint.com`、`w3schools.com`）未過濾
- 過濾後結果為空仍勉強用低質結果填充
- 內嵌引用編號 `[1]`、`[2]` 與末段來源清單編號未一一對應

## 驗證

- [ ] 結果經 `references/source-filter.md` 黑名單過濾，輸出無命中域名
- [ ] 輸出含「來源」段與每筆結果的可點擊 URL，且引用編號與清單一一對應
- [ ] 末段含「使用工具：X」（單工具）或「使用工具：X、Y」（多工具）
- [ ] 未建立任何檔案（不存檔）

## 錯誤處理

- **任何工具失敗**（quota／auth fail／零結果／執行失敗）：fallback 至下一個合理工具，最終 fallback 至 harness 內建 `WebSearch`／`WebFetch`；全部工具失敗時不勉強回低質內容，回報「無高品質結果」並提供 2–3 個候選 query（基於原始 query 的不同關鍵詞組或同義詞）供使用者選
- **使用者要求 codebase 搜尋**：明確告知本 skill 不負責 codebase 範圍

## 延伸參考

- `references/source-filter.md`：劣質網域黑名單清單
- `/find-docs` skill：ctx7 cli 的兩步驟用法（library → docs）
- `exa` MCP: 免認證的 remote MCP，可對 GitHub repo 的 AI 生成文件直接提問
- `DeepWiki` MCP: Exa 官方 MCP server，提供網路搜尋、網頁爬取與深度研究等能力
