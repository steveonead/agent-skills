---
name: ito-explain
description: 探索 codebase 後產出分層解釋，依複雜度分派單 agent 直探或多 explorer 並行後 synthesize，幫助工程師建立子系統心智模型。使用者說「這段怎麼運作」、「解釋這個模組」、「帶我走一次 X 流程」時使用。不適用於需要立即修改程式、純概念性問題、不涉及 codebase 的技術討論、或計畫與設計的壓力測試。
---

# ito-explain

## 概覽

針對 codebase 中的子系統、功能流程、架構或 runtime 行為提出「這段怎麼運作」類問題時，探索實際程式碼並產出供資深工程師 onboarding 等級的解釋，使讀者能建立可操作的心智模型，而非閱讀注釋化原始碼。

## 使用時機

- 使用者問「X 怎麼運作」、「帶我走一次 Y 流程」、「解釋這個模組」
- 陌生 codebase 的子系統需要快速建立心智模型
- 架構面問題，需從多檔多切面整合出單一解釋

**不應使用的情況：** 需要立即修改程式碼（用 `ito-tdd`）、純概念性或理論問題、不涉及具體 codebase 的技術討論、計畫與設計的壓力測試（用 `ito-grill`）。

## 核心流程

### 步驟 1：理解問題並評估複雜度

1. 解析使用者提問類型：子系統、功能流程、架構鳥瞰、runtime trace。
2. **模糊問題分流：** 判別訊號以「是否存在即可」為準，任一訊號命中即歸入對應分類；同時命中兩類時以方向性優先。
   - **方向性歧異**（解讀不同會導致探索路徑完全不同）：先追問使用者釐清，取得答覆後才進入探索。訊號：問題含兩個以上互斥名詞（前端/後端、client/server、讀/寫路徑）；關鍵詞對應 codebase 多個同名子系統（例：存在兩個 `auth` 模組）；或問題未綁定具體入口（「auth 怎麼運作」未指明是登入、rotate token 還是授權檢查）。
   - **範圍歧異**（方向一致、深度未定）：主動猜測並以一句話宣告解讀，直接開始探索，使用者可事後推翻。訊號：問題方向收斂至單一入口但粒度未定（「大概怎麼運作」vs「完整 trace」）；僅層級大小差異；或是否包含邊角情境未明。
3. **評估複雜度：**
   - **Simple**：單一模組、小型工具、範圍窄的函式層級問題。跳至步驟 2b。
   - **Complex**：跨多檔 / 多服務的子系統、cross-cutting feature、完整架構鳥瞰。進入步驟 2a。
4. **宣告分流：** 以一句話告知使用者判定結果與後續動作（例：「判定為 Complex，將派 3 個 explorer 分別處理資料流 / 控制流 / 邊界介面」），使用者可推翻後才執行。
5. **降級規則：** Complex 判定三條件（跨多檔／多服務、cross-cutting、架構鳥瞰）任一不滿足則走 Simple；單 agent 途中遇牆時依錯誤處理章節升級為 Complex。

### 步驟 2a：並行探索（Complex 路徑）

將問題拆為不重疊的探索切面。依問題類型選擇切面數量與優先軸：

| 問題類型 | 切面數 | 優先軸 |
|---|---|---|
| 功能流程（「帶我走一次 X 流程」） | 2–3 | 控制流、資料流；若涉及持久化加狀態管理 |
| 架構鳥瞰（「X 整體架構」） | 3–4 | 邊界介面、資料流、控制流、錯誤處理 |
| 子系統解讀（「解釋 X 模組」） | 2–3 | 邊界介面、控制流；若涉及持久化加狀態管理 |
| Runtime trace（「X 發生時做了什麼」） | 2 | 控制流、錯誤處理 |

切分軸定義：

- **資料流**：資料從何而來、經過哪些轉換、最終落在哪裡
- **控制流**：觸發點、呼叫鏈、分支決策
- **邊界介面**：子系統對外輸入 / 輸出、相鄰子系統的接合面
- **狀態管理**：持久化、快取、運行時狀態變化
- **錯誤處理**：失敗路徑、重試、fallback

若問題類型不落於上表，採預設 2–3 切面並以邊界介面＋控制流為起點。

**Spawn 規則：**

1. 將所有 explorer 在**單一訊息**內 spawn 出去以確保並行。
2. 每個 explorer 為獨立、唯讀的子 agent（Claude Code 使用 `Agent` 工具並以 `subagent_type: Explore`；Codex 使用內建 `explorer` 或具 `sandbox_mode: read-only` 的 agent role）。
3. 每個 explorer 讀取 `references/explorer-prompt.md` 作為基底 prompt，並附上該 explorer 專屬的切面描述與原始問題。
4. **硬門檻：** 每個 explorer 的 Read + Grep + Glob + LSP + ast-grep 總 tool call 達 **30 次**時強制停止並回報。若因門檻停止，explorer 必須於回報中明確標註「因達到 30 次門檻停止」，並於回傳結構中留下 Open Questions。
5. Explorer findings 容許重疊——explainer 會 reconcile。

完成後進入步驟 3。

### 步驟 2b：單 agent 直探（Simple 路徑）

Spawn 單一唯讀子 agent，在同一輪中完成探索與撰寫解釋。該 agent 讀取 `references/explainer-prompt.md` 取得輸出格式與溝通風格，但不需 reconcile 多來源 findings——它的 findings 就是它自己的探索結果。

完成後進入步驟 4。

### 步驟 3：Synthesize（僅 Complex 路徑）

Spawn 單一唯讀子 agent 擔任 explainer，接收所有 explorer findings 並寫出最終解釋。

1. Explainer 讀取 `references/explainer-prompt.md` 取得完整 prompt 模板、輸出格式與溝通風格。
2. **矛盾處理：** Explainer 遇到 findings 矛盾時，能用自身讀碼能力仲裁者，整合為統一敘述，並於對應段落引用仲裁所用檔案路徑與行號作為可驗證痕跡；無法仲裁者，於「眉角」段落明列為「注意：此處不同路徑觀察結果不一致，可能反映 X」。
3. **Gap 處理：** Explainer 有唯讀權限補探 findings 中標註的 Open Questions。若 gap 仍無法解決，於最終輸出誠實揭露。

### 步驟 4：呈現

1. 將 explainer 輸出直接呈現給使用者，允許輕微編輯補對話脈絡，但不實質重寫——explainer 的敘述即產品。
2. **門檻觸發提示：** 若任一 explorer 因 30 次硬門檻停止，於輸出頂端加一段提示：「部分切面探索因達到 30 次 tool call 門檻停止，結果可能不完整。若需更精確的理解，請提供更聚焦的問題（例：限縮特定檔案、特定流程步驟）。」
3. **結果不存檔：** 僅對話呈現，不寫入任何檔案。

## 輸出格式

Explainer 輸出採以下彈性段落結構，依題目性質可省略不適用段落（例：runtime trace 題常不需「關鍵概念」；架構鳥瞰題常不需「眉角」若無歷史背景可談）：

- **概覽**：1–2 段。此 subsystem 是什麼、做什麼、為何存在。
- **關鍵概念**：核心型別 / 服務 / 抽象，簡要定義，僅列理解後續所需。
- **運作方式**：解釋核心，走一次流程。散文為主，不塞 pseudocode 或大段程式碼；引用具體檔案路徑與函式名稱。
- **檔案位置**：簡短檔案 / 目錄圖，只列動工時會碰到的。
- **眉角**：非顯而易見之處、陷阱、歷史脈絡、矛盾 findings。

**產出密度要求：** 每段至少引用 1 個具體檔案路徑或函式名稱，避免空泛架構圖解。

## 搜尋工具選擇

Explorer 與 explainer 在探索 codebase 時依下表選擇工具，避免誤用：

| 工具 | 適用情境 | 範例 | 不適用 |
|---|---|---|---|
| **ast-grep** | 結構型語法模式、跨檔找 AST 形狀 | `ast-grep -p '$A && $A()' -l ts` 找短路守護；`ast-grep -p 'class $X extends $Y' -l ts` 找繼承 | 找檔名、純文字常量、註解內容、不確定語言的混合搜尋 |
| **LSP** | 已有檔案+座標後追符號關係 | `goToDefinition`、`findReferences`、`incomingCalls`、`outgoingCalls` 追呼叫鏈；`workspaceSymbol` 以字串 query 尋符號 | 無座標的零起步搜尋（除 `workspaceSymbol`）、無 LSP server 的語言、純文字搜尋 |
| **Grep** | 純文字 / regex 搜尋 | 找字串常量、註解、config key、log 與錯誤訊息 | 結構模式（改用 ast-grep）、符號關係（改用 LSP） |
| **Glob** | 依檔名模式列檔 | `**/*.ts`、`src/**/Controller.*` | 找檔案內容、找符號 |
| **Read** | 已鎖定目標檔、理解完整實作 | 讀函式 / 型別 / 模組入口，驗證其他工具回傳 | 廣域搜尋、模式匹配 |

**建議流程：** LSP 需先有座標，典型探索路徑為 `ast-grep / Grep / Glob 定位入口 → Read 驗證座標 → LSP 深度追符號關係`。

### 輔助文件探索

探索 codebase 時一併檢查是否有 ADR（Architecture Decision Records）或 DDR（Design Decision Records）文件可作參考。常見位置：

- `docs/adr/`、`docs/decisions/`、`adr/`、`architecture/`、`docs/architecture/`
- `docs/design/`、`docs/rfc/`、`rfcs/`
- 根目錄或 `docs/` 下的 `ARCHITECTURE.md`、`DESIGN.md`

**定位原則：** **以 codebase 為主、文件為輔。** 文件提供設計意圖、歷史脈絡與為何如此的背景；程式碼為實際行為定論。若文件與程式碼不一致，以程式碼為準，並於「眉角」段落標註「文件 X 記載 Y，實作為 Z，可能反映文件過期或實作已偏離」。

## 常見合理化藉口

| 合理化藉口 | 實際情況 |
|---|---|
| 「問題看起來簡單，直接 Simple 就好」 | 未評估複雜度即略過切面拆分會讓跨模組問題走單 agent 路徑，context 爆炸且切面不完整 |
| 「explorer 切面都類似，少拆一個沒差」 | 切面重疊會讓多 explorer 做重工，synthesize 階段也難以分辨真正空缺處 |
| 「findings 矛盾了就挑一個寫」 | 隱藏矛盾會誤導讀者，且失去「矛盾本身即系統理解缺口」的訊號 |
| 「硬門檻 30 次還沒到，繼續挖」 | 門檻是上限非目標，能用更少次完成 trace 即回報——過度探索浪費 token |
| 「使用者問題模糊，我自己解讀開工」 | 方向性歧異未釐清就探索，可能整輪 explorer 白跑 |
| 「explainer 輸出再豐富一點，多加幾段程式碼」 | 過量程式碼稀釋重點；讀者已能自行點檔案路徑查看 snippet，無須原始碼轉貼 |
| 「ADR 寫 X，照 ADR 說明即可」 | ADR/DDR 記錄的是當時的設計意圖，實作可能已偏離。以 codebase 為主、文件為輔；若文件與程式碼不一致，以程式碼為準並於「眉角」段落標註落差 |
| 「找不到 ADR/DDR 就跳過輔助文件」 | 未列出的設計脈絡可能藏在 `ARCHITECTURE.md`、`docs/design/`、根目錄 RFC 等處——至少掃過常見位置再判斷無可用文件 |

## 警訊

- 未宣告複雜度判定結果即 spawn explorer
- 多個 explorer 切面軸重疊（例：兩個都走「資料流」）
- Explainer 輸出全段無具體檔案路徑或函式名稱
- Findings 出現矛盾但未於「眉角」段標註
- Explorer 因硬門檻停止但輸出頂端無提示
- 使用者提問方向性模糊但未追問即開工
- 將解釋寫入檔案（違反「結果不存檔」原則）
- 引用 ADR/DDR 結論但未以程式碼交叉驗證實際行為

## 驗證

- [ ] 步驟 1 的複雜度判定已向使用者宣告
- [ ] Complex 路徑的 explorer 切面軸彼此不重疊
- [ ] Explorer 以單一訊息並行 spawn
- [ ] 每個 explorer 為唯讀子 agent
- [ ] Explainer 輸出每段至少引用 1 個具體檔案路徑或函式名稱
- [ ] Findings 矛盾已於「眉角」段標註，或 explainer 已仲裁並於對應段落留下檔案路徑與行號引用作痕跡
- [ ] 若任一 explorer 因 30 次門檻停止，輸出頂端含提示
- [ ] 結果僅對話呈現，未寫入檔案

## 錯誤處理

- **Explorer 回傳內容過薄或全為 Open Questions：** 沿用原作三層防護——explorer 誠實回報 gaps、explainer 讀碼補 gap、剩餘 gap 在最終輸出透明揭露。不重派 explorer，不降級為 Simple。
- **所有 explorer 皆因 30 次門檻停止：** 於最終輸出頂端以加粗提示使用者探索廣泛受限，建議限縮問題範圍重試。
- **LSP 無對應 server：** 該操作失敗時退回 `Grep` / Read 兜底，於 findings 中註明該語言 LSP 不可用。
- **ast-grep 回傳 0 匹配但預期有：** 確認 `--lang` 旗標正確、pattern 以單引號包裹以避開 shell `$` 展開；必要時改以 Grep 作為兜底。
- **單 agent Simple 路徑遇牆：** 途中發現問題實際上跨多檔多關注點時，回報主 agent 升級為 Complex 路徑。

## 延伸參考

- 計畫或設計的壓力測試，使用 `ito-grill`。
- 以 TDD 實作功能或修 bug，使用 `ito-tdd`。
- `references/explorer-prompt.md`：Complex 路徑 explorer 子 agent 的完整 prompt 模板。
- `references/explainer-prompt.md`：Simple 與 Complex 路徑 explainer 子 agent 的完整 prompt 模板。
