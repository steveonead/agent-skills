---
name: ito-handoff
description: 壓縮當前對話成交接文件，存至 `docs/ito-temp/handoff/`，讓下一個 session 無縫接手。使用者明確說「handoff」、「交接」、「幫忙整理給下一個 session」、或呼叫 `/ito-handoff` 時觸發。不適用於需要直接實作功能、或只是摘要對話內容的情境。
---

# ito-handoff

## 概覽

將當前對話壓縮成交接文件，讓下一個 session 能完整且快速掌握脈絡並繼續工作。

## 使用時機

- 使用者說「handoff」、「交接」、「幫忙整理給下一個 session」
- 當前 session 即將結束，需要保留工作脈絡
- 呼叫 `/ito-handoff [下一 session 目標]`

**不應使用的情況：** 需要直接實作功能、或只是摘要對話內容（無交接意圖）。

## 核心流程

### 步驟 1：確定存檔路徑

以 `[YYYY-MM-DD-HHmm]-[topic-slug].md` 格式產生檔名，存至 `docs/ito-temp/handoff/`。topic-slug 從對話主題推導（小寫、hyphen 分隔）；若主題不明確，以 `session` 作為 slug。若目錄不存在，先建立。

### 步驟 2：撰寫交接文件

依對話內容自由撰寫摘要。若本次為討論型 session，須涵蓋達成共識的決策與未解問題。不重複現有 artifacts（PRD、計畫、ADR、issue、commit），改以路徑或 URL 引用。若使用者傳入 argument，以此為下一 session 的目標焦點調整文件重點。

建議下一 session 可用的 skills（若有）。

### 步驟 3：確認存檔

告知使用者交接文件路徑。

## 常見合理化藉口

| 合理化藉口 | 實際情況 |
|---|---|
| 「對話摘要就夠了」 | 摘要缺少脈絡，下一 session 無法判斷哪些決策已確認、哪些待解 |
| 「已有 PRD，不用再寫」 | PRD 記錄需求，handoff 記錄當前工作狀態與未完成事項 |

## 警訊

- 重複貼出已存在的 artifacts 內容而非引用
- 未告知使用者存檔路徑

## 驗證

- [ ] `docs/ito-temp/handoff/[timestamp]-[slug].md` 已建立
- [ ] 文件涵蓋當前工作狀態與未完成事項
- [ ] 現有 artifacts 以路徑或 URL 引用，未重複貼出內容
