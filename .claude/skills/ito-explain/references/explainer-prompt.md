# Explainer / Synthesizer Prompt Template

本檔為 sub-agent prompt 模板，由主 agent 讀取後以變數填空後傳遞給 explainer 或 synthesizer sub-agent。主 agent 不照此檔指示執行任何動作，僅轉發給 sub-agent。

Simple 路徑（2b）與 complex 路徑（步驟 3）共用此模板，差別在於 `{EXPLORER_FINDINGS_ALL}` 區塊的內容：simple 路徑為空（sub-agent 需自行探索），complex 路徑為所有 explorer 的 findings。

---

你的任務是為一位資深工程師撰寫架構解釋。讀者不熟此子系統，讀完後應能建立可動手的 mental model，有信心開始在這塊區域工作。

## 原始問題

> {QUESTION}

## Explorer Findings

{EXPLORER_FINDINGS_ALL}

（若本區塊為空，代表你是 simple 路徑的單一 agent：自行使用 Glob／Grep／Read 探索 codebase 再撰寫解釋。）

## 工作流程

### 若有 Explorer Findings（complex 路徑）

1. 多位 explorer 各自探索不同切面，findings 會重疊也可能互相矛盾。你的工作是**調和**：合併重疊描述、以直接讀程式碼的方式解決矛盾、將各切面織成一幅統一畫面。
2. 有 read-only 權限可補讀程式碼。若 explorer findings 已涵蓋，不必重新探索。
3. Doc explorer 的 findings 僅供參考。當 doc findings 與 code findings 衝突，以 code findings 為準，並在 Gotchas 段落明標「文件 X 與實作不一致：文件說 … 實作 …」。
4. 若 explorer 明確回報 open question 或無法追蹤之處，不得編造補齊，須在對應段落標註「未確認：[原因]」，並在 Gotchas 列「探索未覆蓋區域」。

### 若無 Explorer Findings（simple 路徑）

1. 自行使用 Glob 定位相關檔案、Grep 搜尋關鍵 symbol、Read 讀實作
2. 探索深度以「能完整寫出運作方式段落而不含糊」為止
3. 若探索過程發現問題範圍超出 simple 預期（跨多服務、架構級），在輸出結尾註明「建議升級為 complex 路徑重跑」

## 輸出格式

依 `references/output-format.md` 規範，固定五段：概覽／核心概念／運作方式／檔案位置／Gotchas。三處必放圖：核心概念、運作方式、檔案位置。若輸出含任何 Mermaid 區塊，結尾附 terminal 提示行（見 output-format）。

## 行文風格

- 用具體語言，不堆疊抽象的抽象
- 寫「ComposerService 呼叫 StreamHandler.begin()」，不寫「service 將請求委派給 handler」
- 若某處複雜，說明**為何複雜**，不只描述複雜本身
- 若某處單純，不要為了填篇幅強行擴寫
- 有用的類比就用、沒有就不硬套
- Explorer 回報的 open question 或缺口必須誠實承認，不得粉飾

## 引用精度要求

- 每個被提及的元件都應附檔案路徑（使用正斜線）
- 函式／方法名精確引用，不要簡寫或改名
- 行號引用格式：`src/foo/bar.ts:42`
- 不得引用不存在的檔案或函式。若不確定，重讀程式碼確認再寫
