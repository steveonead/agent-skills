---
name: ito-tickets
description: 從 PRD 拆出垂直 slice 任務清單，深度探索 codebase 後生成含驗收條件與 size 標籤的可執行任務，迭代確認後存至本地 Markdown 或推送為 GitHub sub-issues。適用於 PRD 完成後需拆任務或轉 GitHub issues 時。不適用於撰寫 PRD、直接實作功能、修改或關閉已建立的 GitHub issues。
---

# ito-tickets

## 概覽

將完成的 PRD 拆成可執行垂直 slice，結合 codebase 深度探索產出有實際檔案脈絡的任務清單，使用者確認後選擇存至本地或開成 GitHub sub-issues。

## 使用時機

- PRD 已完成，需要拆成可由 agent 或開發者逐一執行的具體任務
- 需要將任務轉換成 GitHub sub-issues，並設定原生 blocked-by 依賴關係
- 使用者說「幫我拆任務」、「把 PRD 轉成 issues」、「task breakdown」

**不應使用的情況：** 撰寫或修改 PRD、直接實作功能、純技術架構討論、修改或關閉已建立的 GitHub issues。

## 核心流程

### 步驟 1：讀取 PRD

依 arg 格式自動判斷輸入來源：

- arg 為數字或 issue URL → `gh issue view <number> --comments`
- arg 為檔案路徑 → 讀取本地 Markdown 檔案
- 無 arg → 從對話內容讀取 PRD 描述

### 步驟 2：深度探索 codebase

PRD 讀取後，**必定**執行全面探索：

1. 現有目錄結構與模組邊界
2. PRD 提到的功能是否已有部分實作
3. 相關資料模型、API、元件的現有 pattern
4. 可能受影響的檔案與依賴鏈

### 步驟 3：識別依賴圖

整理各模組間的依賴關係，確認實作順序（以下為通用範例，依實際 codebase 架構調整）：

```
資料 schema
    │
    ├── API 資料模型 / 型別
    │       │
    │       ├── API endpoints
    │       │       │
    │       │       └── Frontend API client
    │       │               │
    │       │               └── UI 元件
    │       │
    │       └── 驗證邏輯
    │
    └── Seed data / migrations
```

實作順序由下往上：先建底層基礎，再往上層延伸。

依賴圖呈現的是**實作順序**，不是任務邊界。建完圖後，確認所有 US 最終落在幾個可獨立 demo 的成果：
- **多個成果**：正常流程，每個成果是一個垂直 slice
- **只有一個成果**：進入單 slice 模式（見步驟 5）

### 步驟 4：逐一確認衝突點

探索完成後，若發現 PRD 與 codebase 有衝突或模糊之處，在產出草稿**前**逐一處理。若無衝突點，直接進入步驟 5。

**每個衝突點的處理方式：**

以決策型格式問一題：
- 說明衝突情境（PRD 說什麼、codebase 現況是什麼）
- 列出 2–4 個互斥選項
- 附上推薦選項與理由

使用者**回答**後，將決策直接納入後續草稿的任務描述與驗收條件，不在草稿中另列 ⚠️。

使用者**跳過**後，保留 ⚠️ 標記，草稿的待確認清單中仍顯示。

全部衝突點解決或跳過後，進入步驟 5。

### 步驟 5：生成計畫草稿

每個任務需貫穿所有需要的層（schema、API、UI、tests），完成後可獨立 demo 或驗證，避免水平切割（例：「建完整 DB schema」後才「建完整 API」）。

以探索結果產出計畫文件，結構依序為：

1. **架構決策**：探索後發現的關鍵架構決策與理由
2. **⚠️ 待確認清單**：步驟 4 逐一確認後仍跳過的衝突點（已解決的直接反映在任務描述中）
3. **任務清單**：垂直 slice 任務，穿插 Checkpoint

讀取 `assets/task-template.md`，依其格式填寫每個任務（標題、描述、驗收條件、Blocked by、Size）。草稿可暫標 XL 表示任務過大需再拆，最終確認前必須拆完。S/M 是 agent 執行效果最佳的範圍。

#### 單 slice 模式

步驟 3 確認只有一個可 demo 的成果時，不因依賴順序明確就按層切。

1. **Schema 獨立條件**：schema 是獨立 package 且有編譯期型別檢查 → 獨立成一個任務，否則整包不拆
2. **其餘部分**：依行為數量決定：
   - 2+ 個可獨立驗收的行為 → 每個行為一個任務
   - 只有 1 個行為 → 整包為一個任務（是自然結果，不是警訊）

| Size | 觸碰檔案數 | 範例 |
|------|----------|------|
| XS | 1 | 新增一條驗證規則 |
| S | 1–2 | 新增一個 API endpoint |
| M | 3–5 | 一個完整 feature slice |
| L | 5–8 | 多元件跨模組功能 |
| XL | 8+ | 太大，須再拆 |

### 步驟 6：草稿迭代確認

呈現完整草稿，詢問使用者：

- 有無 XL 任務須再拆（確認後才可進入步驟 7）
- 粒度是否合理（太粗 / 太細）
- 依賴關係是否正確
- 若有剩餘 ⚠️ 衝突點，確認如何處理
- 需要合併或拆分哪些 slice

反覆調整至使用者確認，再進入步驟 7。

### 步驟 7：選擇輸出方式

使用者確認草稿後，詢問：

> 草稿已完成，要存到本地還是建立 GitHub issues？
> - A）存本地（`docs/ito-temp/tasks/[主題].md`）
> - B）建立 GitHub sub-issues

**本地分支：** 寫入 `docs/ito-temp/tasks/[主題].md`。

**GitHub 分支：** 先讀取 `references/github-api.md` 取得 mutation 範例，再依下列順序執行：

**必須按依賴順序建立 issues**，blockers 先建，才能拿到真實 issue 號碼填入後續的 blocked-by。

1. **確認 parent issue**：有提供 issue 號碼則直接使用。未提供則詢問是否建立新的 PRD parent issue，確認後用 `gh issue create` 建立
2. 每個 issue 用 `gh issue create`，title 格式為 `[#<parent>] Task title`，加上 `Task` 和對應 size label（`size/xs`、`size/s`、`size/m`、`size/l`）
3. 用 `gh api graphql` 執行 `addSubIssue` 將 task issue 掛到 parent
4. 用 `gh api graphql` 執行 `addBlockedBy` 設定依賴關係

## 常見合理化藉口

| 合理化藉口 | 實際情況 |
|-----------|---------|
| 「PRD 很清楚，不需要探索 codebase」 | 不探索就無法識別真實依賴鏈，任務停在抽象層，agent 執行時才發現衝突 |
| 「衝突點不多，跳過步驟 4 直接出草稿」 | 衝突點不解決就會在草稿裡留成模糊假設，迭代確認時更難處理 |
| 「先全部建成 issues，有問題再改」 | GitHub issues 建了不易批次修改，草稿迭代才是正確的確認時機 |
| 「依賴關係很直觀，不用標 Blocked by」 | 隱性依賴在任務多時必出錯，addBlockedBy 的原生關係在 GitHub 上才可視化 |
| 「這個 slice 有點大但還好」 | XL 任務讓 agent 中途迷失，應直接拆成 M 才能可靠執行 |
| 「依賴圖很清楚，照順序切就好」 | 依賴圖是實作順序，不是任務邊界；單 slice 的依賴順序和水平切形狀相同，但意義不同 |

## 警訊

- 跳過 codebase 探索直接生成任務清單
- 有衝突點但跳過步驟 4，直接讓使用者在草稿確認時處理
- 步驟 4 一次問多個衝突點
- 任務之間沒有 Blocked by 關係，但描述裡有「完成後」、「接著」等字眼
- 出現水平切割（「建所有 schema」、「建所有 API」）
- 描述欄出現逐層列舉（建 schema、建 API、建 UI）
- Size 全部標 M，沒有思考拆分可能性
- 推 GitHub 時沒有按依賴順序建立 issues，導致 issue 號碼無法正確填入
- 對既有 issue 執行修改或關閉操作，包含 parent issue
- PRD 只有一個使用者可見的成果，但任務清單按層切（schema 任務 → 後端任務 → 前端任務），每個任務只觸碰單一層

## 錯誤處理

- 若 `gh api graphql` 執行 `addSubIssue` 失敗，確認 parent issue 的 node_id 是否正確後重試；若仍失敗，改以 issue body 補充「Parent: #N」作為 fallback。
- 若 `gh api graphql` 執行 `addBlockedBy` 失敗，在被 block 的 issue body 補上「Blocked by: #N」，並顯示警告提醒使用者手動確認依賴關係是否正確設定。
- 若使用者選擇 B 但 GitHub 操作失敗（repo 不存在、無寫入權限或 API 錯誤），顯示錯誤後詢問是否改以本地分支輸出（`docs/ito-temp/tasks/[主題].md`）。

## 驗證

- [ ] 每個任務有標題、描述、至少兩條驗收條件、Blocked by、Size
- [ ] 無 XL 任務（已拆或已標注原因）
- [ ] 發現衝突點時已執行步驟 4 逐一確認，跳過的項目仍標 ⚠️
- [ ] 推 GitHub 時 issues 依依賴順序建立，Blocked by 關係已用 `gh api graphql` 設定

## 延伸參考

- `references/github-api.md`：addSubIssue 與 addBlockedBy 的 GraphQL mutation 範例
- `assets/task-template.md`：本地 Markdown 中單一任務的格式模板
