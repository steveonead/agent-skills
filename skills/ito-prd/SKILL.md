---
name: ito-prd
description: 對功能需求進行動態訪談，依 template 產出結構化 PRD，可存至本地或發為 GitHub Issue。支援新增與編輯兩種模式，輸入不拘：空白需求、文件、現有 PRD 路徑或 issue 皆可。使用者說「幫我寫 PRD」、「建立 PRD」、「編輯 PRD」或提到產品需求文件、功能規格時使用。不適用於 bug 修復、重構規劃、技術調研、純討論、或需求已明確不需訪談。
---

# ito-prd

## 概覽

對功能需求進行動態訪談，產出符合 `assets/prd-template.md` 的結構化 PRD。支援新增與編輯兩種模式，輸入形態不拘，輸出目的地可選本地檔案或 GitHub Issue（兩擇一）。與其他 skill 不強耦合。

## 使用時機

- 使用者說「幫我寫 PRD」、「建立 PRD」、「編輯 PRD」、「改一下這份 PRD」
- 需要將功能需求展開為正式 spec
- 輸入可以是：空白需求、需求文件、現有 PRD 路徑（e.g., `docs/prd/xxx.md`）、或 GitHub issue URL / 編號

**不應使用的情況：** bug 修復、重構規劃、技術調研、需求已明確不需訪談。已有明確 issue 要拆 task 請用 `prd-to-issues`；無需結構化需求的純討論請用 `ito-grill`。

## 核心流程

### 步驟 1：模式判斷

依 args 形態自動判斷：

- args 為 issue 編號（`#123`）、issue URL（`https://github.com/.../issues/123`）、或含 `/` 或 `.md` 的 local path → **編輯模式**
- 空 args 或純文字描述 → **新增模式**

### 步驟 2：新增模式開場（依 args 形態分流）

僅新增模式執行。依 args 形態決定第一題策略：

- **空 args** → 使用開放型問題：「你想做什麼？」
- **空泛需求**（一句話描述）→ 以該需求當起點，第一題追問情境（e.g.「你目前在什麼情況下遇到這個？」）
- **引入文件 / URL** → 先讀取文件內容，從中挑 2-3 個最關鍵或最不確定的點反饋給使用者，再開始訪談

**引入的文件只作為背景材料，訪談仍從頭走**：不預填 template 欄位，所有 PRD 都經過完整訪談以避免隱性假設。

### 步驟 3：編輯模式讀入

僅編輯模式執行。依輸入來源讀取：

- issue 來源 → 執行 `gh issue view <number> --json title,body,labels` 取得內容
- local 來源 → 讀取指定檔案

讀入後詢問使用者：「你想改哪幾段 / 新增什麼？」後進入步驟 4。

### 步驟 4：動態訪談

沿用 `ito-grill` 的訪談風格與問題格式（決策型 / 現況確認型 / 開放型）。若需確認格式細節，讀取 `.claude/skills/ito-grill/SKILL.md` 或 `skills/ito-grill/SKILL.md` 的「問題格式」章節以擷取格式模板。

**四條守則：**

1. 一回合只問一題。
2. 每當前一個決策解鎖新子問題，先用一句話宣告依賴關係，再提下一題。
3. 若問題可透過探索 codebase 回答，優先探索，不直接問使用者：
   - 單一明確查詢（e.g., 找一個 function 名稱）→ 直接用 Grep / Glob
   - 範圍不確定或需要多輪搜尋 → 使用 sub-agent（Explore 類型），避免污染主對話 context
4. 根據問題性質選擇對應格式（決策型要附推薦與理由；現況確認型不附推薦；開放型不列選項）。

**訪談結構原則：**

- **全面訪談，不綁 template 欄位順序**：agent 從對話中萃取並歸納成 template 結構
- 允許發散討論以碰撞不同想法，最後由 agent 整理收斂
- 每收集完一個 User Story 後，追問「還有其他角色 / 場景 / 流程嗎？」
- 使用者回答「沒有」後，主動掃描角色覆蓋（e.g.「目標涉及 admin，但還沒有 admin 的 US，要補嗎？」）

**編輯模式額外守則：** 優先處理使用者指向的改動（步驟 3 的回覆），再由 agent 對照收斂標準掃描全文，列出未達標處逐題追問。兩條線並行。

### 步驟 5：收斂判斷與銜接

**收斂標準（三者皆須滿足）：**

1. Template 所有必填欄位皆有實質內容（Open Questions 選填，允許空）
2. 每個 AC 必須包含完整的「前提 / 動作 / 結果」三欄
3. agent 已主動掃描未談分支（錯誤情境、權限邊界、資料遷移、並發、rate limit、空狀態等）

達到收斂標準後，使用 `ito-grill` 的收斂提示格式：

```
訪談已接近收斂，目前還有 X 個未解問題待確認：
 - A）[未解問題 1]
 - B）[未解問題 2]
 - C）進入下一步
```

使用者選 C（或喊「可以了」）後進入步驟 6。

### 步驟 6：Review（table + 摘要）

**不顯示完整 PRD 內容。** 以兩張表 + 摘要呈現：

**上表：收斂標準檢核**

| # | 標準 | 狀態 | 摘要 |
|---|------|------|------|
| 1 | 必填欄位都有內容 | ✓ | [一句摘要] |
| 2 | AC 都有前提/動作/結果 | ✓ | [一句摘要] |
| 3 | 未談分支主動掃描 | ✓ | [一句摘要] |

**下表：US/AC 檢核**

| US# | 標題 | AC 數 | 邊界覆蓋 |
|-----|------|-------|----------|
| US-01 | [標題] | 2 | Y |
| US-02 | [標題] | 3 | Y |

**整體摘要（3-5 句）**：濃縮問題描述、Out of Scope、已知侷限的關鍵點。

### 步驟 7：Review 打回處理

若使用者指出某個欄位 / US / AC 不對：

- **小修改**（錯字、一句話調整）→ agent 就地修改內部狀態，重新產出 table + 摘要
- **大修改**（新增 US / AC、改變收斂判斷、補充新分支）→ 回到步驟 4 針對該段訪談

agent 依使用者描述推斷走哪種，使用者可 override（e.g.「我想重新 grill 這段」）。修改完成後重跑步驟 6。

### 步驟 8：輸出

依模式分流：

- **新增模式**：詢問使用者選「local 或 issue」（兩擇一，無 both）
- **編輯模式**：**無選擇**，回寫到輸入來源（issue 進 → 更新原 issue；local 進 → 覆蓋原檔案）

填入 template 前讀取 `assets/prd-template.md` 取得結構，再填入訪談結果。所有文字使用繁體中文台灣用語，proper nouns 保留英文。

**填入前自行檢查：**

- 四個必填 section 皆存在：`## 問題描述`、`## User Stories`、`## Out of Scope`、`## 已知侷限`
- 至少一條 User Story 以 `**US-XX ` 格式開頭（XX 為兩位數編號）
- 每個 section 內容非 placeholder 殘留（e.g.「[一到兩句說明...]」不得殘留）

若任一項未通過，回步驟 4 補問缺漏。

**Local 輸出細節：** 讀取 `references/output-local.md` 以掌握路徑、命名、gitignore 提醒等規則。

**Issue 輸出細節：** 讀取 `references/output-issue.md` 以掌握 title 生成、label 處理、重複檢查、發送流程。

**Issue 回寫細節（僅編輯模式 issue 來源）：** 讀取 `references/output-issue.md` 的「回寫流程」一節，取得 diff 展示與覆蓋步驟。

### 步驟 9：邊界銜接（stand-by）

寫入或發送完成後：

1. 展示最終 artifact 位置（檔案絕對路徑 / issue URL）
2. 提示：「review 完有想改的告訴我。」
3. skill **stand-by**：不主動結束、不主動追問、不列下一步 pipeline 清單
4. 若使用者回覆要改 → **直接進入步驟 3 的編輯模式流程**，以剛產出的 artifact 作為來源（不需使用者重新下 args）
5. 若使用者無反饋或明確說「沒問題」→ 流程自然結束

## 常見合理化藉口

| 合理化藉口 | 實際情況 |
|---|---|
| 「使用者貼了文件，先幫他填欄位省時間」 | 步驟 2 明確規定文件只當背景；預填會遺漏隱性假設 |
| 「使用者說可以了，就不用再問」 | 收斂判斷由 agent 主導（步驟 5），確認三項標準都達到再銜接 |
| 「技術問題查一下 codebase 就好，不用問使用者」 | 步驟 4 守則 3 允許探索 codebase 的客觀問題；但使用者偏好 / UX 決策仍要問 |
| 「編輯模式使用者只說改 AC，就只改 AC」 | AC 變動常連動功能範圍或已知侷限；agent 要主動掃描連動影響 |
| 「新增模式也可以同時發 issue 又存 local」 | 步驟 8 明確規定兩擇一，無 both；使用者若想要兩份，下一輪改用編輯模式 |
| 「Review 時直接秀完整 PRD，比較清楚」 | 步驟 6 規定只秀 table + 摘要；完整內容 review 延後到寫入後 |
| 「寫入後 skill 就結束，使用者要改自己重跑」 | 步驟 9 明確規定 stand-by，使用者回覆要改直接進入編輯模式 |
| 「issue body 可以加 summary / metadata 讓使用者一眼看懂」 | `references/output-issue.md` 規定 body 為 template 原樣，不加任何額外區塊 |

## 警訊

- 一回合出現兩個以上問題
- User Stories 只有功能級別（「使用者可以登入」），缺乏「前提 / 動作 / 結果」三欄驗收條件
- PRD 沒有 Out of Scope section
- 訪談中使用者貼新文件時重啟訪談，而非併入既有 context
- 步驟 6 的 review 顯示完整 PRD 內容，而非 table + 摘要
- 步驟 8 新增模式提供「both」選項
- 步驟 8 編輯模式詢問使用者輸出目的地（應直接回寫來源）
- 步驟 9 寫入後 skill 主動結束，未 stand-by
- Issue body 含 template 外的區塊（summary、front matter、附錄等）
- 發 issue 時未檢查重複 PRD
- `PRD` label 不存在時未自動建立，直接發 issue 且不貼 label

## 驗證

- [ ] 步驟 1 模式判斷正確（args 形態 → 模式對應）
- [ ] 新增模式開場依 args 形態分流（步驟 2）
- [ ] 訪談全程一回合一題，問題格式符合 ito-grill 三種格式之一
- [ ] 收斂標準三項皆達成（必填欄位 / AC 完整 / 未談分支掃描）
- [ ] 步驟 6 的 review 僅顯示兩張表 + 3-5 句摘要，未顯示完整 PRD
- [ ] 步驟 7 review 打回後重跑步驟 6，而非直接跳到輸出
- [ ] 新增模式輸出為 local 或 issue 兩擇一（無 both）
- [ ] 編輯模式輸出為回寫來源（無三選一）
- [ ] Template 所有必填 section 皆填入非 placeholder 內容
- [ ] 每條 User Story 都有編號、標題、主述句、「前提/動作/結果」驗收條件
- [ ] 若發 issue：title 以 `[PRD]` 開頭、貼 `PRD` label、body 為 template 原樣（無額外區塊）
- [ ] 若編輯 issue：已展示 diff 並取得使用者同意後才覆蓋
- [ ] 步驟 9 寫入後 skill stand-by，未主動結束

## 錯誤處理

- 若 `gh issue create` / `gh issue edit` 失敗：檢查 `gh auth status`，保留記憶體中的 draft，提示使用者執行 `! gh auth login` 後再試
- 若 `gh label create` 失敗（無權限等）：警告使用者並繼續發 issue，但不貼 label
- 若 `docs/prd/` 或使用者指定的父目錄不存在：自動建立目錄後再寫入
- 若使用者在訪談中途說「先跳過這題」：記錄為未解問題，計入步驟 5 的 X 值
- 若使用者回答「我不知道」：先用反向問題追問（從結果、影響或相反情境切入）；若依然不知道，記錄為未解問題或 Open Questions 後繼續訪談
- 若使用者回答超出選項範圍：不直接接受後進下一題，根據該回答追問釐清技術含義或決策影響
- 若編輯模式的 issue number / local 路徑不存在或無法讀取：回報錯誤，要求使用者確認來源或重新提供
- 若訪談中使用者中途貼新文件 / URL：agent 接收為背景補充，併入後續訪談，不重啟

## 延伸參考

- 訪談風格與問題格式：參照 `ito-grill` skill
- PRD 拆解為實作 issue：參照 `prd-to-issues` skill
- Local 輸出細節：讀取 `references/output-local.md`
- Issue 輸出與回寫細節：讀取 `references/output-issue.md`
- Template 結構：讀取 `assets/prd-template.md`
