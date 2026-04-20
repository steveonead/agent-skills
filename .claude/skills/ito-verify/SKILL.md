---
name: ito-verify
description: 根據 GitHub PRD Issue 掃描 codebase 的 AC 覆蓋率 gap，自動補 integration test 並跑 MCP 互動驗證，失敗則開 bug issue。使用者說「幫我驗收」或從 ito-implement 結束後銜接時觸發。不適用於尚未完成所有 sub-issue、一般 bug 修復或重構驗證。
---

# ito-verify

## 概覽

讀取 GitHub PRD Issue 的 User Stories / Acceptance Criteria，掃當下 codebase 找出 AC 覆蓋率 gap，自動補 integration test（非 UI 行為）與 MCP 互動驗證（UI 行為），失敗的 AC 開成獨立 bug issue，並在 parent PRD 追加 verify comment。

## 使用時機

- 使用者說「幫我驗收」、「跑 PRD 驗證」
- `/ito-implement` 跑完所有 sub-issues 後
- 修完 bug issue 後要 re-run 驗收

**不應使用的情況：** 尚未有 PRD Issue、sub-issues 尚未全部 closed、一般 bug 修復驗證、重構驗證、E2E 驗證（由工程師另行判斷）。

---

## 核心原則

1. **PRD level，不看 slice 層**：只看 PRD 的 US / AC，不管 task 怎麼切。
2. **Coverage gap based**：每次執行都重新掃當下 codebase，不維持 state，不讀上次結果（避免 snapshot 過期）。
3. **Full re-scan on re-run**：re-run 也重新掃整份 PRD，失敗 bug issue 的 lifecycle 靠 `## 驗證對照` 對齊。
4. **前端兩種手段**：integration test（非 UI 行為）+ MCP 互動驗證（UI 行為）。E2E 不在 skill 範圍。
5. **全跑完再報告**：gap 執行失敗不中斷，所有驗證跑完才彙整。

---

## 核心流程

### 步驟 1：驗證 argument

檢查是否有 `<prd-issue-number>` argument：

- 有 argument → 繼續步驟 2
- 無 argument → 報錯並中止：

  > 請提供 PRD issue number：`/ito-verify <prd-issue-number>`

### 步驟 2：讀取 PRD issue

```bash
gh issue view <prd-issue-number> --json title,body,labels,state
```

驗證 labels 包含 `PRD`，否則中止：

> Issue #<n> 沒有 `PRD` label，`/ito-verify` 僅驗證 PRD issue。

從 body 解析 User Stories 與 Acceptance Criteria 區塊。每條 AC 記錄：
- `index`：AC 在 PRD 中的順序（1-based）
- `text`：AC 原文
- `hash`：`text` 的 SHA-1 前 8 碼（供 re-run 對齊）

### 步驟 3：Hard gate — sub-issues 必須 closed

```bash
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
gh api repos/${REPO}/issues/<prd-issue-number>/sub_issues \
  --jq '[.[] | select(.state == "open")]'
```

- 若有任何 open sub-issue → 列出後中止：

  > 以下 sub-issues 尚未 closed，請先完成實作再執行 `/ito-verify`：
  > - #X [title]
  > - #Y [title]

- 全 closed → 繼續步驟 4

### 步驟 4：偵測可用 MCP 與 test conventions

**4a. MCP 偵測**

掃當前 session 可用的瀏覽器 / UI 互動類 MCP（e.g., playwright、chromium、browser）。取偵測結果中優先序最高者，記錄名稱供步驟 7 使用。若無可用 MCP，標記為「無 MCP」，UI gap 在 plan mode 將被標示為無法自動驗證。

| MCP | 架構 | Context 成本 | 跨瀏覽器 | 適用情境 |
|---|---|---|---|---|
| Playwriter MCP | Chrome extension + WebSocket relay，連使用者現有 Chrome；單一 `execute` tool | 低 | 僅 Chromium（需 extension） | 預設首選：保留登入/cookies、可觀察並介入 agent 操作 |
| Playwright MCP | MCP server + Playwright API，a11y tree 導向，70+ 細分 tools | 中高 | Chromium / Firefox / WebKit | Playwriter 不可用時備援；需跨瀏覽器驗證 |
| Chrome DevTools MCP | MCP server + Puppeteer + CDP，主打 Performance trace / Lighthouse / 網路診斷 | 中 | 僅 Chrome / Chrome for Testing | 不列入 AC 互動驗證優先序；僅供效能診斷輔助 |

**4b. Monorepo / convention 偵測**

讀取 `references/monorepo-detection.md` 以提取 workspace 列舉策略與 per-package runner / test 位置推斷規則。執行偵測後產出下列結構：

```
packages:
  - name: <package-name>
    path: <relative-path>
    runner: <jest|vitest|mocha|...>
    test_dir: <relative-path>
    test_command: <command>
```

若 repo 根目錄存在 `.claude/ito-verify.config.json`，優先讀取該檔的 packages 設定，偵測結果僅作為 diff 提示。

### 步驟 5：查詢既有 bug issues

查詢本 PRD 相關的 bug issues（包含 closed）：

```bash
gh issue list \
  --label bug \
  --state all \
  --search "\"PRD：#<prd-issue-number>\" in:body" \
  --json number,state,body,title
```

對每個結果解析 body 中的 `## 驗證對照` 區塊，提取：
- `prd`：PRD issue number（對應「PRD：#<n>」）
- `ac_index`：AC 在 PRD 中的順序（對應「AC 編號：<n>」）
- `ac_hash`：AC 文字 hash（對應「AC 雜湊：<hash>」）

過濾掉 `prd` 不等於 `<prd-issue-number>` 的 issue（search 可能誤中）。產出 existing_bugs 清單。

### 步驟 6：Sub-agent 掃 gap + 分類

Spawn sub-agent（Explore 類型），輸入：
- 所有 AC（index / text）
- 偵測到的 packages 與 test conventions
- Repo 目錄結構摘要

要求 sub-agent 對每條 AC 回傳：
- `covered`：是否已被現有測試（unit / component / integration）語意覆蓋
- `category`：`ui` 或 `non-ui`（UI 需要瀏覽器互動才能驗證 → `ui`，否則 `non-ui`）
- `focus_package`：若為 `non-ui`，推論 test 應落在哪個 package（依 AC 驗證焦點，資料落地 → backend、互動流程 → frontend、schema 驗證 → shared）
- `proposed_test`：若為 gap，提議 test 名稱與驗證動作摘要（一句話）

Sub-agent 回傳後，主流程執行**對齊**（不動 sub-agent context）：

| 對齊情況 | 條件 | 動作 |
|---|---|---|
| **Matched + still gap** | existing_bug 的 `ac_index` + `ac_hash` 皆對得上，且本次判為 gap | 標記為 `reopen-candidate` |
| **Matched + now covered** | existing_bug 對得上，但本次判為 covered | 標記為 `close-candidate` |
| **AC edited** | `ac_index` 對得上但 `ac_hash` 不同 | 標記為 `warn-edited`，plan mode 提示 |
| **AC deleted（orphan）** | existing_bug 的 `ac_index` 已超過本次 AC 總數，或該 index 被不同 hash 占據且未配對 | 標記為 `warn-orphan`，plan mode 提示 |
| **New gap** | 本次判為 gap，無任何 existing_bug 對上 | 標記為 `new-gap` |

### 步驟 7：進入 plan mode，呈現 gap list + re-run diff + override

進入 plan mode，呈現下列區塊：

```
PRD #<n>：[title]
總 AC 數：N
MCP：<偵測到的名稱，或「無」>

Packages（偵測結果）：
  - frontend (apps/web) — vitest, apps/web/tests/integration/
  - backend (apps/api) — jest, apps/api/tests/integration/
  - shared (packages/schema) — vitest, packages/schema/__tests__/

[ ] 將上述偵測結果存成 .claude/ito-verify.config.json

Gap 清單：
  1. [non-ui/frontend] AC#3 「提交表單後顯示成功訊息」
     提議 test：apps/web/tests/integration/submit-form.test.ts
  2. [ui]           AC#5 「錯誤狀態下按鈕顯示紅色邊框」
     提議 MCP 驗證：playwright 互動
  3. [non-ui/backend] AC#7 「送出無效 payload 回傳 400」
     提議 test：apps/api/tests/integration/validate-payload.test.ts

Re-run diff（相對上次執行）：
  ⚠️  AC#2 文字被編輯，對應 bug issue #123
      舊 hash: abc12345 / 新 hash: def67890
      選擇：[y] 沿用 issue #123 / [n] 當新 AC / [s] skip 此 AC
  ⚠️  Bug issue #99 對應的 AC 已從 PRD 移除（orphan）
      舊 AC#4 hash: 11112222
      選擇：[c] close issue / [k] keep open / [s] skip
  ℹ️  上次失敗 AC#5 本次仍為 gap → 驗證後若仍失敗將 reopen issue #105
  ℹ️  上次失敗 AC#3 本次 re-verify 後若 pass → 將 auto-close issue #102

Override：
  - skip：輸入 "skip AC#<n>" 從本次執行移除該 gap
  - 改分類：輸入 "reclass AC#<n> ui|non-ui [package]"
  - 手動追加：輸入 "add AC#<n> [ui|non-ui] [package] [test-name]"

確認後退出 plan mode 開始執行。
```

工程師確認後退出 plan mode；若中止，整個 skill 停止。工程師的 override 與 edited / orphan 的選擇會併入執行計畫。

### 步驟 8：退出 plan mode，執行驗證

依 gap 清單**依序**執行（不中斷於失敗）：

**Non-UI gap（integration test）：**
1. 依 `focus_package` 與對應 package 的 convention，在 test_dir 下建立 test 檔
2. 測試內容由 sub-agent 的 `proposed_test` 展開為完整 test code，遵循該 package 既有 test 風格
3. 執行 `test_command`，記錄 pass / fail + 輸出

**UI gap（MCP 互動驗證）：**
1. 依 MCP 工具啟動互動 session
2. 依 AC 描述執行互動步驟（導航、點擊、輸入、assert）
3. 記錄 pass / fail + 截圖 / 錯誤訊息

**若步驟 4a 標記「無 MCP」**：UI gap 全數標記為 `unverifiable`，不嘗試執行，後續報告中註明。

若工程師選擇了「存成 config」，在執行前寫入 `.claude/ito-verify.config.json`。

### 步驟 9：報告 + bug issue lifecycle

**9a. Bug issue 對齊動作**

| 對齊類型 | 動作 |
|---|---|
| `close-candidate` + 本次 pass | `gh issue close`，追加 comment：「Verified passed on <ISO-date> by /ito-verify」 |
| `reopen-candidate` + 本次 fail | 若 issue 為 closed 則 `gh issue reopen`；追加 comment 記錄本次 failure evidence 與 `Last verified` 時間 |
| `new-gap` + 本次 fail | 以 `assets/bug-issue.template.md` 建立新 issue，label `bug`，body 含 `## 驗證對照` |
| `warn-edited` 工程師選 `y` | 更新舊 issue 驗證對照中的「AC 雜湊」欄位，追加 comment「AC 文字已更新」 |
| `warn-edited` 工程師選 `n` | 舊 issue 不動，當 `new-gap` 流程處理本次 AC |
| `warn-orphan` 工程師選 `c` | `gh issue close`，comment 註明 AC 已從 PRD 移除 |
| `warn-orphan` 工程師選 `k` / `s` | 不動舊 issue |
| `unverifiable` UI gap | 不開 bug issue，僅在報告中列出 |

**9b. 終端 summary**

```
/ito-verify #<n> 完成
總 AC：N
  ✓ Covered（含本次新補）：X
  ✗ Fail：Y（bug issue #A, #B）
  ⚠ Unverifiable（無 MCP）：Z
  ⊘ Skipped：W

Bug issue 變動：
  auto-closed: #102
  reopened:    #105
  new:         #130, #131
  orphan:      #99 (closed per user choice)
```

**9c. Parent PRD comment**

以 `assets/prd-verify-comment.template.md` 為模板，追加 comment 到 PRD issue：

```bash
gh issue comment <prd-issue-number> --body-file <rendered-template>
```

---

## 常見合理化藉口

| 合理化藉口 | 實際情況 |
|---|---|
| 「re-run 太慢，只跑上次 fail 的 AC 就好」 | 跳過 full re-scan 會漏抓 regression（既有代碼被改壞），違反 coverage gap based 核心原則 |
| 「有 open sub-issue 但只剩 1 個，先驗證再說」 | Hard gate 存在是為了避免把「還沒做」誤判成「gap」，絕不例外 |
| 「orphan bug issue 不理會就好」 | 累積的 orphan 會讓後續 re-run 的 diff 越來越混亂 |
| 「這條 AC 的 test 應該放兩個 package，都補吧」 | 覆蓋兩次會變成重複測試，違反 focus_package 的單一落點設計；若真的兩邊都驗證，plan mode 用 `add AC#<n>` 明確手動追加 |
| 「E2E 也順便補一下」 | E2E 不在 skill 範圍，由工程師在 PR 流程外判斷 |

## 警訊

- Hard gate 被繞過（有 open sub-issue 仍繼續）
- 同一條 AC 在 existing_bugs 匹配到多筆 issue（資料不一致）
- Sub-agent 回傳的 `focus_package` 不在偵測到的 packages 清單中
- `## 驗證對照` 區塊解析失敗（舊 issue 格式不同）→ 應當成 orphan 處理
- Plan mode 未呈現 Re-run diff 區塊但 existing_bugs 非空
- UI gap 被標為 `unverifiable` 但流程嘗試執行 MCP
- Test 寫入 package 的 test_dir 以外路徑

## 驗證

- [ ] Hard gate 已檢查所有 sub-issues 皆 closed
- [ ] MCP 偵測結果已在 plan mode 呈現（或註明「無」）
- [ ] Packages 與 test conventions 偵測結果已在 plan mode 呈現
- [ ] Re-run diff 已列出所有 `warn-edited` / `warn-orphan` / `reopen-candidate` / `close-candidate`
- [ ] 工程師對 `warn-edited` 與 `warn-orphan` 的選擇已記錄
- [ ] 驗證全跑完才進入報告（未因單一 gap 失敗中斷）
- [ ] Bug issue lifecycle 動作對齊步驟 9a 表格
- [ ] Parent PRD comment 已追加

## 錯誤處理

- `gh issue view` 失敗 → 提示 `! gh auth login`，中止
- `gh api .../sub_issues` 失敗（repo 未啟用 sub-issues）→ 改問工程師「是否所有相關 task issues 均已 closed？」，以人工確認取代 hard gate
- Workspace 偵測失敗（無 workspace config、看似 single package）→ 退回單 package 模式，僅偵測 repo 根目錄 convention
- 工程師在 plan mode 輸入無法解析的 override → 再次呈現 plan mode，標示無法解析的輸入
- 測試寫入後 `test_command` 找不到指令 → 標記該 gap 為 `unverifiable`（執行環境問題），不中斷其他 gap

## 延伸參考

- 進入此 skill 前，使用 `/ito-implement` 完成所有 sub-issues
- `/ito-verify` 與 `/ito-review` 獨立，不 block（review 聚焦 PR 品質，verify 聚焦 PRD 覆蓋）
- `references/monorepo-detection.md`：workspace 列舉與 per-package runner / test 位置推斷規則
- `assets/bug-issue.template.md`：Bug issue body 格式（含 `## 驗證對照`）
- `assets/prd-verify-comment.template.md`：Parent PRD verify comment 格式
