---
name: ito-pr
description: 從 git 變更與 commit 歷史自動產生 GitHub PR title 與 body，含雙確認流程、語言與 scope 偵測、行為變更區塊、影片或截圖建議與 issue refs。適用於使用者說「開 PR」、「建立 PR」、「更新 PR」、「open PR」、「create PR」、「update PR」。支援 `--draft`、`--target`、`--rewrite`。不適用於需要 fork PR 或從 default branch 開 PR 的情境。
---

# ito-pr

## 概覽

從目前 branch 的 commits 與 diff 推導 PR title 與 body，套用 repo PR template 或內建 template，提供雙確認流程（預覽 → push）後呼叫 `gh` 建立或更新 PR。具備變更類型偵測、行為變更區塊、影片或截圖建議、issue refs 與既有手動內容保留。

## 使用時機

- 使用者說「開 PR」、「建立 PR」、「更新 PR」、「open PR」、「create PR」、「update PR」
- 使用者輸入 `/ito-pr`、`/ito-pr --draft`、`/ito-pr --target develop`、`/ito-pr --rewrite`
- 需要將目前 branch 的變更整理成 PR title 與 body 並推送

**不應使用的情況：** 需要從 default branch（main/master）開 PR、需要 fork repo 對上游開 PR、需要設定 reviewer/assignee/label、僅需 commit 不需要 push 或建 PR。

## 參數

| 參數 | 說明 |
|------|------|
| `--draft` | 建立 draft PR（預設為正式 PR）|
| `--target <branch>` | 指定 target branch，跳過自動偵測 |
| `--rewrite` | 跳過 slot 保留邏輯，整份 body 重寫（更新模式才有意義）|

## 核心流程

### 步驟 1：Preflight 檢查

依序執行以下檢查，任一失敗即中止並提示。

**1.1 gh CLI 可用性：**

```bash
gh --version
gh auth status
```

未裝 → 提示 `brew install gh`。未登入 → 提示 `gh auth login`。

**1.2 基本 git 資訊：**

```bash
git rev-parse --abbrev-ref HEAD
git status --short
git remote get-url origin
```

**1.3 Default branch 守門：**

判斷 `origin` 的 default branch（`gh repo view --json defaultBranchRef -q .defaultBranchRef.name`）。若當前 branch 等於 default branch，**中止**並列出建議的 branch 命令：

```
不可從 default branch 開 PR。請先建立 feature branch：

  git checkout -b <suggested-name>

建議名稱：<type>/<module>-<短描述>
依據第一個 commit subject 與主要變更模組推導。
```

`<suggested-name>` 從目前未推送的 commits 推導：取首個 commit 的 conventional type（feat/fix/...）+ diff 中變更行數最多的模組目錄名 + commit subject 關鍵字（最多 3 字）。

**1.4 Working tree 狀態：**

- `git status --short` 為空且 `git log @{u}..HEAD` 也為空 → 中止，提示「無相對於 base 的 commits」
- 有未提交變更 → 提示先 commit 或 stash 後再執行
- 無 upstream（`git rev-parse --abbrev-ref @{u}` 失敗）→ 步驟 5 時補 `-u` push

**1.5 Fork 偵測：**

```bash
gh repo view --json isFork,parent
```

若 `isFork == true` 且 parent 存在 → 中止並提示「不支援 fork PR，請在 upstream repo 直接操作」。

**1.6 Repo PR template 偵測：**

```bash
gh api repos/{owner}/{repo}/contents/.github/PULL_REQUEST_TEMPLATE.md 2>/dev/null
```

未命中時退而查 `.github/PULL_REQUEST_TEMPLATE/` 資料夾，取第一個 `.md` 檔。仍未命中時改用內建 `references/pr-template.md`。記住此次採用的 template 來源。

**1.7 既有 PR 偵測：**

```bash
gh pr view --json number,title,body,url,baseRefName,state 2>/dev/null
```

- 命中且 `state == OPEN` → 進入**更新模式**
- 命中但 `state` 為 `CLOSED` 或 `MERGED` → 中止，提示「既有 PR 已關閉/合併，請建立新 branch」
- 未命中 → 進入**建立模式**

### 步驟 2：偵測語言與 scope 樣式

僅學語言與 scope，不學 body 語氣（避免仿造劣樣本）。

**2.1 語言偵測：**

```bash
gh pr list --limit 5 --json title,body
```

統計近 5 筆 PR 的 title 與 body 主要語言。

- 全部或多數為繁體中文 → 沿用中文
- 全部或多數為英文 → 沿用英文
- 無樣本（新 repo）→ fallback 繁體中文（zh-tw）
- 混合 → 取多數，平手時 fallback 繁體中文

**2.2 Scope 樣式偵測：**

從同一批 PR 抽取 title 中 `<type>(<scope>): ...` 的 scope 段。

- 多數 scope 與 branch name 高度相似（含 prefix 如 `feature/`、`fix/`）→ scope 用 **branch name**
- 多數 scope 為短小模組關鍵字（如 `auth`、`media`）→ scope 用 **module**
- 無樣本或不一致 → fallback **module**：從 diff 中變更行數最多的模組目錄名取一個簡短關鍵字

### 步驟 3：蒐集 diff 與生成內容

**3.1 取得變更資料：**

決定 target branch：

- 有 `--target` → 用指定值
- 有既有 PR → 用其 `baseRefName`
- 否則自動偵測：對每個 remote branch 計算 `git rev-list --count <branch>..HEAD`，取最小者

```bash
git log --oneline <target>..HEAD
git diff <target>...HEAD --stat
git diff <target>...HEAD
```

Diff 超過 500 行時截斷，保留 stat 全文。

**3.2 變更類型偵測（emoji checkbox）：**

可同時勾選多項。沿用以下判斷：

| 類型 | 判斷條件 |
|------|----------|
| 🐛 Bug 修復 | commit message 含 `fix`，或修改了明顯的 bug 修復邏輯 |
| ✨ 新功能 | commit message 含 `feat`，或新增了檔案與功能模組 |
| 💄 UI/Style 更新 | 修改了 `.css`/`.scss`/`.vue` 的 style 區塊 |
| ♻️ 重構 | commit message 含 `refactor`，或大量重新組織程式碼 |
| 📝 文件更新 | 修改了 `.md` 檔案或 JSDoc 註解 |
| 🔧 設定調整 | 修改了設定檔（`.json` config、`.env`、`vite.config` 等）|
| 🚨 測試相關 | 修改或新增了測試檔（`*.spec.*`、`*.test.*`）|
| 🔥 程式碼移除 | 刪除了檔案或大量移除程式碼 |
| ⚡️ 效能改善 | commit message 含 `perf`，或明確的效能改善 |

未勾選項目仍保留在 body 中（方便使用者事後在 GitHub 上補勾）。

**3.3 PR title：**

格式：`<type>(<scope>): <描述>`

- `<type>`：選自 feat/fix/refactor/style/docs/chore/perf/test/remove，依勾選的變更類型決定主要 type
- `<scope>`：依步驟 2.2 結果（branch name 或 module）
- `<描述>`：依步驟 2.1 語言，簡潔概述整體變更，首行 ≤ 72 字元

**3.4 PR body 結構：**

讀取步驟 1.6 決定的 template 來源（repo template 優先，否則讀取內建 `references/pr-template.md`）。填入：

- **變更類型 checkbox**：依 3.2 結果勾選，全 9 項保留
- **描述**：依下列規則生成

**Body 描述規則：**

預設「summary + bullets」結構：

1. 1–3 句 summary 開頭，總結 PR 目的與整體變更
2. 主要變更分點（bullets），引用路徑時用 backticks

升級為**編號區段**的觸發條件（任一命中即升級）：

- 變更類型 checkbox 勾選 ≥ 2 → 每個勾選類型獨立一個編號區段
- 單一類型但變更檔案 ≥ 10 或變更行數 ≥ 500 → 依模組分區，每個模組一個編號區段

編號區段格式：

```markdown
### 1. ✨ <區段標題>

<該區段說明>

- <要點 1>
- <要點 2>
```

**3.5 行為變更區塊（條件性加入）：**

掃描 diff，依下表觸發。兩組獨立判斷，都命中時兩區塊都出。

**UI 情境格式 trigger：**

| 偵測條件 | 範例 |
|----------|------|
| 修改檔含 `.vue`/`.tsx`/`.svelte`、且涉及使用者互動 | dialog、filter、navigation 邏輯 |
| Conditional display 規則變更 | `isVisible`、`isDisabled`、`v-if`/`v-show` 條件邏輯修改 |
| 預設 UI 行為改變 | 預設值、預設選項、初始狀態變更 |
| 按鈕行為或表單提交邏輯改變 | onClick、submit handler、redirect 路徑 |

命中時加入 `## 操作流程與情境`，每個情境含背景、操作步驟（3–5 步）、新行為附「觸發此情境的關鍵改動」，原有行為標註 `（原有行為，繼續相容）`。

**Before/after fenced trigger：**

| 偵測條件 |
|----------|
| API contract 變動（route、method、status code 對應）|
| Output shape 變動（response payload schema、欄位增減）|
| Config 變動（環境變數、設定檔欄位）|
| CLI output 格式變動 |
| Request payload schema 變動 |
| Permissions 或權限規則變動 |
| Input format 變動（接受的參數格式或 validation 規則）|

命中時加入 `## Before / After` 區塊，每組變動列 before 與 after 的 fenced code block：

```markdown
## Before / After

### <變動標題>

Before:
\`\`\`<lang>
<舊內容>
\`\`\`

After:
\`\`\`<lang>
<新內容>
\`\`\`
```

**3.6 影片或截圖建議（條件性）：**

步驟 3.5 的 UI 情境 trigger 命中時，生成 `## 影片或截圖` 建議文字：

- 從 3.5 偵測到的具體 UI 情境（dialog、filter、navigation 等）推導描述，說明「建議補上哪些操作畫面」
- 命中 trigger 但無法推導具體情境時（例如純樣式調整），填入：「此 PR 涉及 UI 樣式調整，建議確認視覺呈現是否符合預期」
- 生成內容前加入 sentinel：`<!-- ito-pr:auto -->`

此邏輯適用於建立模式與更新模式。trigger 未命中時不執行，slot 保持 `無`。

**3.7 Issue refs：**

掃描以下來源中的 issue 參照：

- 當前 branch name
- 步驟 3.1 取得的所有 commit messages

匹配 pattern：`#\d+` 與 `[A-Z]+-\d+`（Jira 樣式）。

多個 ref 全部列出。預設動詞用 `Refs`（保守，不自動 close）。

```markdown
---

Refs #123 #456 PROJ-789
```

若無偵測到任何 ref，省略此區段。

### 步驟 4：預覽與第一次確認

展示完整預覽，明確標示操作模式、target、是否 draft。

**建立模式：**

```
PR 預覽（建立新 PR）

Title:  <title>
Target: <target>（自動偵測 / 指定 / 既有 PR）
Mode:   正式 PR / Draft PR
Template: repo / 內建

---
[完整 PR body]
---

確認預覽？(y / 修改 / n)
```

**更新模式：**

```
PR 預覽（更新既有 PR #<number>）

Title:  <title>
Target: <target>
URL:    <url>
Rewrite: 是 / 否（slot 保留）

---
[完整 PR body]
---

確認預覽？(y / 修改 / n)
```

收到 `y` → 進入步驟 5。收到「修改」或具體調整指示 → 依指示調整後重新預覽。收到 `n` → 中止。

### 步驟 5：第二次確認後 push 與建立/更新

**5.1 Push 確認：**

若需要 push（無 upstream，或本地領先 upstream）：

```
即將執行：
  git push -u origin <branch>

確認 push？(y / n)
```

收到 `y` 才執行 push。`n` 中止。

**5.2 建立或更新 PR：**

**建立模式：**

```bash
# 正式 PR（預設）
gh pr create --base <target> --title "<title>" --body "$(cat <<'EOF'
<body>
EOF
)"

# Draft PR（--draft 時）
gh pr create --base <target> --draft --title "<title>" --body "$(cat <<'EOF'
<body>
EOF
)"
```

**更新模式：**

```bash
gh pr edit <number> --title "<title>" --body "$(cat <<'EOF'
<body>
EOF
)"
```

**5.3 回報結果：**

顯示 PR URL 與操作結果（已建立 / 已更新）。

### 步驟 6：更新模式的 slot 保留

更新模式且**未指定** `--rewrite` 時，從既有 PR body 解析以下三個固定 heading，若使用者有手動填入非預設值，保留至新 body 對應位置：

| Heading | 預設值（視為未填）|
|---------|------------------|
| `## 影片或截圖` | `無`、空白、缺少此段（sentinel 內容見下方特殊邏輯）|
| `## 規格文件連結` | `無`、空白、缺少此段 |
| `## 補充說明` | `無`、空白、缺少此段 |

`## 影片或截圖` 的特殊邏輯：

- 開頭含 `<!-- ito-pr:auto -->` → 視為 auto-generated，重新執行步驟 3.6（trigger 未命中時 3.6 回傳 `無`）
- 無 sentinel 且非空白/`無` → 視為使用者手動填入，保留，不執行步驟 3.6

其他區塊（變更類型 checkbox、描述、行為變更、Refs）一律 rewrite。

`--rewrite` 指定時：跳過此步驟，整份 body 完全重寫。

## 邊際情況處理

- **多 template 資料夾版本**：`.github/PULL_REQUEST_TEMPLATE/` 下多檔時，取第一個 `.md`（依檔名排序）
- **既有 PR 已 closed/merged**：步驟 1.7 中止，提示新開 branch
- **0 commits 但 dirty working tree**：步驟 1.4 中止，提示先 commit 或 stash
- **沒有 commits 相對於 base**：步驟 1.4 中止
- **gh 未裝或未登入**：步驟 1.1 中止，列安裝/登入命令
- **fork PR**：步驟 1.5 中止，不支援

## 常見合理化藉口

| 合理化藉口 | 實際情況 |
|------------|---------|
| 「使用者已說 y，可直接 push 並建 PR」 | 第一次 y 只批准預覽，push 需第二次 y，雙確認不可合併 |
| 「default branch 上有 commits，照樣開 PR 即可」 | 步驟 1.3 必須中止並提示建立 feature branch，不繞過 |
| 「Body 結構固定用編號區段比較整齊」 | 預設 summary + bullets，僅在 3.4 升級條件命中時升級，避免單一變更過度結構化 |
| 「行為變更區塊兩組都加保險」 | 兩組各自有觸發條件，未命中就不加，避免空殼區塊 |
| 「更新模式直接 rewrite 比較乾淨」 | 預設保留三個固定 slot 的使用者手動內容，`--rewrite` 才繞過 |
| 「Issue ref 用 `Closes` 比較主動」 | 預設 `Refs` 保守，不自動 close 避免誤觸發 |
| 「沒偵測到 scope 就空著」 | fallback module，從變更行數最多的目錄取關鍵字 |
| 「Fork PR 也是 PR，照流程跑」 | 步驟 1.5 偵測 fork 即中止，不支援 |

## 警訊

- 在 default branch 上未中止直接呼叫 `gh pr create`
- 跳過步驟 4 預覽直接 push 或 create
- 跳過步驟 5.1 push 確認直接執行 `git push`
- 預覽時未標示 target branch、操作模式或 draft 狀態
- 更新模式未保留三個固定 slot 的非預設內容（且未指定 `--rewrite`）
- 更新模式中 `## 影片或截圖` slot 有 `<!-- ito-pr:auto -->` sentinel，卻未重新執行步驟 3.6
- 更新模式中 `## 影片或截圖` slot 無 sentinel 的使用者內容被覆蓋
- UI 情境 trigger 命中時 `## 影片或截圖` slot 未填入含 sentinel 的建議文字
- Body 仿造近期 PR 語氣（學風格只限語言 + scope）
- Issue ref 預設用 `Closes`/`Fixes` 而非 `Refs`
- Title 超過 72 字元
- Fork repo 上仍嘗試開 PR

## 驗證

- [ ] 第一次 `y` 後才呈現 push 確認。第二次 `y` 後才執行 push 與 `gh pr create`/`gh pr edit`
- [ ] PR URL 已輸出，與 `gh pr view --json url` 一致
- [ ] 建立模式無指定 `--draft` 時為正式 PR（`isDraft == false`）
- [ ] 更新模式未指定 `--rewrite` 時，三個固定 slot 的非預設內容已保留
- [ ] UI 情境 trigger 命中時，`## 影片或截圖` slot 填入開頭含 `<!-- ito-pr:auto -->` 的建議文字；trigger 未命中時 slot 保持 `無`
- [ ] Default branch 上呼叫時已中止並列出建議 branch 名

## 錯誤處理

- 若 `gh pr create`/`gh pr edit` 失敗，顯示完整錯誤訊息，不重試也不掩蓋，常見原因列出（網路、權限、branch 已被刪除、target branch 不存在）
- 若 `git push` 失敗，顯示錯誤後中止，提示檢查 remote 設定與 upstream
- 若步驟 1.6 的 `gh api` 因權限或 repo private 失敗，靜默 fallback 至內建 template，不中止流程

## 延伸參考

- `references/pr-template.md`：內建 PR body template，repo 無 `.github/PULL_REQUEST_TEMPLATE.md` 時讀取
