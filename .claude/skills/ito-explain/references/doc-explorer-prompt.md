# Doc Explorer Prompt Template

本檔為 sub-agent prompt 模板，由主 agent 讀取後以變數填空後傳遞給 doc explorer sub-agent。主 agent 不照此檔指示執行任何動作，僅轉發給 sub-agent。

---

你的任務是探索 codebase 內的架構文件（ADR、DDR、設計文件、README 等），找出與原始問題相關的設計意圖、架構決策與歷史脈絡。

**重要定位：** 你的 findings 僅供參考，權威以 code explorers 的實際探索為準。Synthesizer 將以 code findings 為主，你的 findings 用於補脈絡、回溯動機。衝突時以 code 為準。請在 findings 首行明寫本段定位。

## 原始問題

> {QUESTION}

## 探索範圍

優先檢查下列路徑（存在才讀，不存在即略過）：

- `docs/**/*.md`、`doc/**/*.md`
- `adr/`、`adrs/`、`decisions/`、`rfc/`、`rfcs/`
- root 層：`ARCHITECTURE.md`、`DESIGN.md`、`README.md`、`CONTRIBUTING.md`
- `CLAUDE.md`、`AGENTS.md`（部分 repo 將設計決策寫此）

找不到任一類文件時，回傳「findings 為空：此 codebase 未發現架構文件」，不得編造。

## 探索指示

1. 用 Glob 盤點上述路徑的檔案清單
2. 用 Grep 在所有 markdown 內搜尋與原始問題關鍵詞相關的段落
3. 讀取命中的檔案，擷取與問題直接相關的架構決策、設計意圖或約束說明
4. 僅引用文件原文或摘要，不自行推斷「因此程式碼應該長怎樣」

## 限制

- 僅使用 read-only 工具：Glob、Grep、Read
- 不修改任何檔案
- 不讀取程式碼檔案（`.ts`、`.py`、`.go` 等），程式碼探索由 code explorers 負責
- 若文件中含程式碼片段，可引用該片段作為文件佐證，但不得另行追蹤原始碼實作

## 輸出格式

以下列結構回傳 findings。首行必須為定位聲明。

### 定位聲明

> 本 findings 為架構文件探索結果，僅供參考。權威以 code explorers 的程式碼探索為準；衝突時以程式碼為準。

### 文件清單

列出探索到的所有相關文件：路徑 + 一句話摘要。

### 架構決策

從 ADR／DDR／RFC 擷取的明確決策：決策標題、決策內容、決策日期（若可得）、所在檔案。

### 設計意圖

文件中對本問題相關子系統的設計意圖、目標、約束說明。附檔案路徑與引文。

### 與問題相關的脈絡

任何有助於理解「為何這樣設計」的歷史或背景資訊。附來源。

### 未解問題

文件中提到但未完整說明的設計點，或文件之間互相矛盾之處。
