---
name: ito-explain
description: 解釋 codebase 中某功能、子系統或流程如何運作。派出平行 sub-agent 探索程式碼與架構文件，產出含 ASCII／Mermaid 圖、資料流與設計決策的架構解釋。使用者說「解釋 X 怎麼運作」、「X 架構長怎樣」、「走過 X 的完整流程」、「帶讀 X 的原理」時使用。不適用於需要修改程式碼、實作新功能、跨 codebase 的純技術概念問答、≤10 行片段的逐行註解。
---

# ito-explain

## 概覽

在當前 codebase 探索程式碼與架構文件，為「X 怎麼運作」這類問題產出含資料流與設計決策的架構解釋。產出含「核心概念」「運作方式」「檔案位置」三處流程圖，讀完即可建立可動手的 mental model。

## 使用時機

- 使用者想了解某功能、子系統或流程在此 codebase 中如何運作
- 使用者要求 onboarding 級別的架構說明（「幫忙了解這塊怎麼跑」「整體架構長怎樣」）
- 使用者要求某個 runtime trace（「當使用者按下送出按鈕後發生什麼事」）

**不應使用的情況：** 需要修改程式碼、實作新功能、修 bug 的任務；跨 codebase 的純技術概念問答（「React 的 reconciler 怎麼運作」這類非本 codebase 範疇的問題）；僅需對 ≤10 行程式片段做逐行註解的任務（本 skill 目標是架構級理解，不是 code review）。

## 核心流程

### 步驟 1：解析問題並判斷複雜度

1. 解析使用者問題，辨識探索範圍。可能形式：
   - 子系統級：「訊息虛擬化怎麼運作」
   - 功能流程級：「on-demand 計費怎麼處理」
   - 架構總覽級：「auth service 架構長怎樣」
   - Runtime trace 級：「使用者送出訊息後完整流程」
2. 若範圍模糊，採用最佳猜測並以一句話宣告詮釋（例：「我將此題解讀為 Y，若不符請中斷」），不向使用者追問，直接開始探索，讓使用者自行 redirect。
3. 依下列啟發式判定 simple 或 complex：
   - **Simple**：單一模組、小工具、窄問題（例：「函式 X 怎麼運作」「util Y 做什麼」）→ 跳至步驟 2b
   - **Complex**：跨多檔案／多服務的子系統、跨切面功能、整體架構概覽 → 進入步驟 2a
   - 曖昧時倒向 simple，後續若 agent 回報 context 不足再升級。

### 步驟 2a：平行探索（complex 題才執行）

1. 將問題拆成 2–4 個互斥探索角度，每個 explorer 負責一個 slice。分工依題目決定，以下為典型範例：
   - 前端元件／UI 子系統 → 資料模型、渲染管線、事件／互動
   - API／後端流程 → 請求入口、業務邏輯、資料層 & 外部整合
   - 背景 job／pipeline → 觸發條件、執行邏輯、錯誤處理 & 重試
   - 若題目不符上述三類，主 agent 自行拆出 2–4 個互斥切面，只要切面互不重疊且合計能覆蓋題目即可
2. 在**同一則訊息**派出所有 explorer（含 1 個 doc explorer），共 3–5 個 sub-agent 平行：
   - Code explorers（2–4 個）：`subagent_type=general-purpose`，每個 explorer 收到 `references/explorer-prompt.md` 全文 + 該 explorer 的指派角度
   - Doc explorer（固定 1 個）：`subagent_type=general-purpose`，收到 `references/doc-explorer-prompt.md` 全文。用來探索 `docs/`、`adr/`、`decisions/`、`rfc/`、root 層 `ARCHITECTURE.md`／`DESIGN.md`／`README.md`／`CLAUDE.md` 等架構文件，所得 findings 僅供參考
3. 所有 explorer 回傳後，進入步驟 3。

### 步驟 2b：直接探索並解釋（simple 題才執行）

1. 派出單一 sub-agent（`subagent_type=general-purpose`），由該 agent 自行完成探索與解釋：
   - 該 agent 收到 `references/explainer-prompt.md` 全文 + `references/output-format.md` 全文 + 原始問題
   - 該 agent 直接使用 Glob／Grep／Read 探索 codebase，無需等 explorer findings
2. 該 agent 輸出即為最終解釋，跳至步驟 4。

### 步驟 3：收斂（complex 題才執行）

1. 派出單一 synthesizer sub-agent（`subagent_type=general-purpose`），輸入：
   - 所有 code explorer 的 findings
   - Doc explorer 的 findings（明標「僅供參考，code 為準」）
   - `references/explainer-prompt.md` 全文
   - `references/output-format.md` 全文
2. Synthesizer 負責：
   - 整合重疊 findings、解決矛盾
   - 必要時自行 Read 程式碼補洞
   - 當 doc findings 與 code findings 衝突，以 code 為準，並在 Gotchas 段落明標「文件 X 與實作 Y 不一致：文件說 … 實作 …」
   - 產出符合 `references/output-format.md` 規範的最終解釋
3. Synthesizer 輸出即為最終解釋，進入步驟 4。

### 步驟 4：呈現並詢問存檔

1. 將最終解釋原樣呈現給使用者。可為語意通順做輕度潤飾，不做結構性改寫。
2. 若解釋中包含任何 Mermaid 區塊，在解釋結尾附下列提示行（逐字）：
   > 此回覆含 Mermaid 圖，terminal 僅顯示原始碼；存檔後於 IDE／GitHub 預覽可看渲染版。
3. 呈現後詢問使用者：「要將此解釋存至 `docs/explain/[主題].md` 供日後參考嗎？」
4. 若使用者選擇存檔：
   - 依原始問題關鍵詞 slugify 自動命名（例：「解釋訊息虛擬化」→ `docs/explain/message-virtualization.md`）
   - 若關鍵詞過於抽象或無法明確 slugify，轉向「錯誤處理」對應條目向使用者確認檔名
   - 若 `docs/explain/` 不存在，先建立目錄
   - 寫檔後回報路徑

## 具體模式與規範

### 圖必放段落（三處）

依 `references/output-format.md` 規範，下列三段落**必須含至少一張圖**：

| 段落 | 強制圖型 |
|---|---|
| 核心概念 | Mermaid `classDiagram` 或 `erDiagram`（呈現型別／模組關係） |
| 運作方式 | 按流程型態挑（見下表） |
| 檔案位置 | ASCII tree |

### 運作方式段落圖型對應

| 流程型態 | 圖型 | 理由 |
|---|---|---|
| 時序／簡單線性呼叫鏈 | ASCII 箭頭圖 | terminal 直接可讀，Mermaid 過度包裝 |
| 多角色互動時序 | Mermaid `sequenceDiagram` | 呈現 actor 間訊息往返 |
| 含狀態／多分支決策 | Mermaid `flowchart` | 分支視覺化 ASCII 難以表達 |
| 類別／模組關係 | Mermaid `classDiagram`（若屬核心概念段落已畫則不重複） | 關係線條 ASCII 表達力不足 |

### Sub-agent 派遣規則

- Complex 題一律在**同一則訊息**派出所有 sub-agent（code explorers + doc explorer），以觸發 harness 平行執行
- Explorer 之間 findings 重疊可接受，由 synthesizer 調和
- 不指定 sub-agent 的 model 參數，讓 harness 依預設挑選
- 探索類 sub-agent 僅需 read-only 權限，實作上以 `general-purpose` 配合 prompt 明示「僅探索、不修改」即可

## 常見合理化藉口

| 合理化藉口 | 實際情況 |
|---|---|
| 「問題很窄，直接回答就好，不派 sub-agent」 | Skill 要求一律走 2a 或 2b，跳過會讓解釋流於猜測，無法 ground 到實際程式碼 |
| 「prose 已經寫清楚了，圖可以省」 | 三處段落的圖為硬性規範，省略會讓使用者失去視覺對照，違反 skill 核心價值 |
| 「題目類型不在三類範例內，乾脆不派 explorer」 | 主 agent 應自行拆切面，切面互斥且合計覆蓋題目即可，不派等於跳過 2a |
| 「complex 題派 1 個 explorer 就夠」 | 單 explorer 容易漏視角，2–4 個平行才能覆蓋跨檔案／跨服務的 slice |
| 「doc explorer 沒找到文件就不附了」 | 找不到文件本身是重要訊號（代表此子系統無 ADR 可參考），仍要明標於輸出 |
| 「doc 寫得很清楚，code 看不到就照 doc 寫」 | 權威以 code 為準，doc 僅供參考；衝突必須在 Gotchas 標出「文件與實作不一致」 |
| 「範圍有點模糊，先問使用者再開始」 | 明確禁止追問，模糊時採最佳猜測並宣告詮釋，由使用者 redirect |
| 「使用者沒明說要圖，不用加」 | 圖屬結構性輸出，由 skill 強制而非使用者要求驅動 |

## 警訊

- 解釋輸出缺少「核心概念」「運作方式」「檔案位置」三處任一的圖
- Complex 題只派 1 個 sub-agent（應為 3–5 個平行）
- Simple 題派 3 個以上 explorer（應為 1 個）
- Synthesizer 直接複製貼上 explorer findings 未調和
- Doc findings 與 code findings 衝突時未在 Gotchas 標示
- 範圍模糊時向使用者追問而非宣告詮釋
- 輸出含 Mermaid 區塊但未附 terminal 提示行
- 使用者選擇存檔但未建立 `docs/explain/` 目錄

## 驗證

- [ ] 依 simple／complex 正確走 2b 或 2a 路徑
- [ ] Complex 題在同一則訊息派出 3–5 個 sub-agent（含 1 個 doc explorer）
- [ ] Simple 題僅派 1 個 sub-agent
- [ ] 最終解釋含五段：概覽／核心概念／運作方式／檔案位置／Gotchas
- [ ] 核心概念段含 Mermaid `classDiagram` 或 `erDiagram`
- [ ] 運作方式段含依流程型態挑選的圖
- [ ] 檔案位置段含 ASCII tree
- [ ] 含 Mermaid 區塊時，輸出結尾含 terminal 提示行
- [ ] 呈現後主動詢問使用者是否存檔
- [ ] 若使用者選擇存檔，檔案寫入 `docs/explain/[主題].md` 並回報路徑

## 錯誤處理

- **Explorer 回傳空手或明確回報 context 不足**：Synthesizer 在對應段落標註「未確認：[原因]」，並在 Gotchas 段落列「探索未覆蓋區域」；不自行編造補齊。
- **Doc explorer 找不到任何架構文件**：在輸出結尾 Gotchas 段列「此 codebase 未發現 ADR／架構文件，解釋全以程式碼為據」。
- **Synthesizer 自行補洞後仍無法確定**：在對應位置明標不確定性（例：「此處實際觸發條件未能完全確認，疑似為 X」），讓使用者有機會自行查證。
- **使用者選擇存檔但主題命名不明**（步驟 4.4 bullet 2 的例外分支）：列出 2–3 個候選檔名（基於原始問題不同關鍵詞組）讓使用者選擇，寫檔前取得明確確認。
- **原問題在 simple 路徑下 agent 回報需升級為 complex**：重新走步驟 2a，不沿用 simple 路徑既有輸出。
