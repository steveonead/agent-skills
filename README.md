# ITO Agent Skills

## 快速安裝

透過 [`npx skills`](https://github.com/vercel-labs/skills)（Open Agent Skills CLI）可將本 repo 的 skill 安裝到其他專案或使用者全域：

```bash
# 互動式新增：挑選要安裝的 skill
npx skills add steveonead/agent-skills

# 互動式更新：從來源 repo 重新拉取已安裝的 skill
npx skills update

# 互動式刪除：從已安裝的 skill 中選擇要移除的項目
npx skills remove
```

更多參數請見 [vercel-labs/skills](https://github.com/vercel-labs/skills) 文件。

---

## 建議搭配安裝

ito-* 流程會搭配以下工具使用，建議一併安裝：

| 工具 | Repo | 簡介 |
|---|---|---|
| **Context7** | [upstash/context7](https://github.com/upstash/context7) | 為 LLM 取得最新官方文件的 CLI 與 skill，避免以訓練資料猜測 API 或語法。 |
| **DeepWiki MCP** | [CognitionAI/deepwiki](https://github.com/CognitionAI/deepwiki) | 免認證的 remote MCP，可對 GitHub repo 的 AI 生成文件直接提問。 |
| **Exa MCP** | [exa-labs/exa-mcp-server](https://github.com/exa-labs/exa-mcp-server) | Exa 官方 MCP server，提供網路搜尋、網頁爬取與深度研究等能力。 |
| **ast-grep** | [ast-grep/ast-grep](https://github.com/ast-grep/ast-grep) | 以 AST pattern 進行結構化程式碼搜尋與改寫的 CLI 工具。 |
| **Playwriter** | [remorses/playwriter](https://github.com/remorses/playwriter) | 透過 Chrome 擴充功能在本機瀏覽器執行 Playwright 片段的 CLI。 |

---

## 本機輸出與 .gitignore

部分 skill 會在當前專案的 `docs/` 底下產生 markdown 檔案，多屬個人草稿或驗收紀錄，不一定需要進版控。建議依實際需求加入 `.gitignore`：

| 路徑 | 來源 skill | 用途 |
|---|---|---|
| `docs/idea/` | `ito-grill` | 訪談收斂後的摘要 |
| `docs/prd/` | `ito-prd` | 存於 local 的 PRD 文件 |
| `docs/verify/` | `ito-browser-verify` | UI 驗收報告 |

範例 `.gitignore` 片段：

```
docs/idea
docs/prd
docs/verify
```

---

## 開發生命週期

```
┌─ Define ──────────────┐   ┌─ Plan ────┐   ┌─ Build ─┐   ┌─ Verify ──────────┐   ┌─ Ship ────┐
│ ito-grill ─▶ ito-prd  │─▶ │ito-issues │─▶ │ ito-tdd │─▶ │ito-browser-verify │─▶ │ito-commit │
└───────────────────────┘   └───────────┘   └─────────┘   └───────────────────┘   └───────────┘
                                                 ▲                  │
                                                 │                  │
                                                 └── Fail：Prove-It ┘
                                                         Spec
```

另有 Meta skill `ito-create-skill`，橫跨所有階段，供建立與審查 skill 本身。

每個 skill 代表一段獨立流程。使用者可從任一階段開始，也可依箭頭方向接續執行。當 `ito-browser-verify` 驗證失敗時，會產出 TDD Prove-It Reproduction Spec，回饋至 `ito-tdd` 作為下一輪 failing test 的起點。

---

## Slash Commands 總覽

| Slash Command | 階段 | 核心用途 |
|---|---|---|
| `/ito-grill` | Define | 逐一追問決策分支，壓力測試計畫或釐清需求 |
| `/ito-prd` | Define | 將需求訪談收斂為結構化 PRD，存至 local 或建立 gh issue |
| `/ito-issues` | Plan | 讀取 PRD issue，拆成可獨立 demo 的 vertical slice sub-issues |
| `/ito-tdd` | Build | 以紅綠重構流程開發新功能；修 bug 時採用 Prove-It 變體 |
| `/ito-browser-verify` | Verify | 透過瀏覽器工具依 AC 執行 UI 層整合驗證，產出結構化報告 |
| `/ito-commit` | Ship | 掃描 git 工作區改動並依語意分組，生成 Conventional Commits 計畫 |
| `/ito-create-skill` | Meta | 依 agentskills.io 規範撰寫或審查 skill 本身 |

---

## Skills 個別說明

### 1. 釐清需求 - [`ito-grill`](.claude/skills/ito-grill/SKILL.md)

**做什麼**
- 依決策樹逐分支追問，與使用者達成共識
- 收斂後可選擇將摘要存至 `docs/idea/`

**使用時機**
- 使用者說「我想討論」、「幫我釐清」
- 需求模糊、需要壓力測試計畫或驗證假設

### 2. 產生 PRD - [`ito-prd`](.claude/skills/ito-prd/SKILL.md)

**做什麼**
- 逐題訪談收斂為結構化 PRD，包含 User Stories、AC、Out of Scope、已知侷限
- 支援新增與編輯兩種模式
- 最後存至 `docs/prd/`，或建立 gh issue（帶 `PRD` label 與 `[PRD-{編號}]` 前綴）

**使用時機**
- 使用者說「寫 PRD」、「整理需求」、「開需求 issue」
- 使用者說「編輯 issue 的 PRD」

### 跟據 PRD 拆任務 - [`ito-issues`](.claude/skills/ito-issues/SKILL.md)

**做什麼**
- 讀取 PRD issue，以 read-only 方式探索 codebase
- 切分 vertical slice sub-issues
- 以 GitHub 原生 sub-issue 與 Blocked by 建立依賴
- Title 格式為 `[PRD-<parent>/<index>]`

**使用時機**
- 使用者說「把 PRD 拆成 task」、「建 sub-issue」
- `ito-prd` 完成後接著拆 task

### 3. 執行 TDD - [`ito-tdd`](.claude/skills/ito-tdd/SKILL.md)

**做什麼**
- 須先完成 Planning（interface、behaviors、priority）並取得批准
- 以 tracer bullet 逐條執行 RED → GREEN → REFACTOR
- 修 bug 時採用 Prove-It 變體：先撰寫能重現問題的 failing test，再修改程式碼

**使用時機**
- 使用者明確要求「TDD」、「先寫測試」、「紅綠重構」、「Prove-It」
- 需要測試先行的情境

### 4. 驗證 UI/UX - [`ito-browser-verify`](.claude/skills/ito-browser-verify/SKILL.md)

**做什麼**
- 依驗收標準（GitHub issue、local markdown 或對話提供）產出 Planning 並取得批准
- 透過 `/playwriter` 或其他瀏覽器工具逐條驗證
- 失敗項目收集 evidence 並產出 Prove-It Reproduction Spec
- 最終寫入 `docs/verify/[slug]-[timestamp].md`

**使用時機**
- 使用者要求「做 UI 驗證」、「驗收 PRD 或 issue」
- 使用者說「用瀏覽器驗剛完成的功能」

### 5. Git Commit 分組 - [`ito-commit`](.claude/skills/ito-commit/SKILL.md)

**做什麼**
- 讀取 `git diff` 與 `git log`，自動偵測 commit message 語言
- 依語意分組產出 Conventional Commits 計畫
- 使用者 A／B 確認後依序執行；`--fast` 標記可將改動合併為單一 commit
- 不執行 `git push`、不使用 `git add -A`

**使用時機**
- 整理工作區多個性質不同的改動
- 小幅改動想快速提交

### 6. 建立新 SKILL - [`ito-create-skill`](.claude/skills/ito-create-skill/SKILL.md)

**做什麼**
- 依 agentskills.io 規範建立新 skill，含 metadata 驗證、目錄結構、progressive disclosure
- 審查既有 skill，依 rubric 產出含嚴重度標註的 inline findings 報告

**使用時機**
- 需要建立新 skill
- 需要審查既有 skill 的合規與設計邏輯

---

## Skill 之間的關係

### 線性流程

```
ito-grill ──▶ ito-prd ──▶ ito-issues ──▶ ito-tdd ──▶ ito-browser-verify ──▶ ito-commit
 (釐清)        (PRD)       (拆 task)      (實作)        (UI 驗收)             (送出)
```

各 skill 的 SKILL.md 已內建主動接手規則：

- `ito-grill` 收斂後使用者說「那來寫 PRD」，`ito-prd` 主動接手。
- `ito-prd` 完成後使用者說「接著拆 task」，`ito-issues` 主動接手。

### 非線性回饋

```
ito-browser-verify ──── Prove-It Spec ──▶ ito-tdd
 (Fail 報告)                                (Prove-It 變體)
```

`ito-browser-verify` 產出的報告會在失敗項目附上「失敗操作序列 + failure signature + URL/user/state context + 相關 API response 或 DOM 節點」，可直接作為 `ito-tdd` Prove-It 變體的 failing test 起點，形成驗證與修復的完整循環。

### 隨時可切出的橫向支援

- **`ito-grill`**：在 `ito-prd`、`ito-issues`、`ito-tdd` 任一階段遇到需求不明或設計分歧時，使用者可主動切換釐清，完成後再回原流程。
- **`ito-create-skill`**：當上述任一 skill 需要調整或新增時，透過 Meta 流程處理，避免直接修改而破壞既有契約。

---

## 專案結構

```
.claude/skills/
├── ito-grill/
│   └── SKILL.md
├── ito-prd/
│   ├── SKILL.md
│   └── assets/prd-template.md
├── ito-issues/
│   ├── SKILL.md
│   └── references/
│       ├── issue-template.md
│       ├── vertical-slicing-examples.md
│       └── re-run-precheck.md
├── ito-tdd/
│   ├── SKILL.md
│   └── references/
│       ├── interface-design.md
│       ├── mocking.md
│       ├── refactoring.md
│       └── tests.md
├── ito-browser-verify/
│   ├── SKILL.md
│   ├── assets/report-template.md
│   ├── scripts/make-slug.sh
│   └── references/
│       ├── input-resolution.md
│       ├── non-ui-classification.md
│       └── evidence-checklist.md
├── ito-commit/
│   ├── SKILL.md
│   └── references/output-template.md
└── ito-create-skill/
    ├── SKILL.md
    ├── assets/SKILL.template.md
    ├── scripts/validate-metadata.sh
    └── references/
        ├── checklist.md
        └── review-rubric.md
```

每個 skill 遵循 progressive disclosure：`SKILL.md` 為進入點與主邏輯，`references/` 存放依需載入的背景資料，`assets/` 存放輸出模板，`scripts/` 存放確定性邏輯工具。

---

## 設計原則

所有 ito-* skill 皆依循 `ito-create-skill` 所訂的四大原則：

1. **流程而非散文** — Skill 是 agent 執行的工作流程，每份都具備步驟、檢查點與結束條件，而非供人閱讀的參考文件。
2. **反合理化機制** — 每份 skill 附一張「常見合理化藉口」表，列出 agent 可能用來跳過步驟的藉口，並提供對應反駁。
3. **驗證不可妥協** — 每份 skill 結尾要求具體證據（測試通過、建置輸出、執行時資料），僅憑「看起來沒問題」不足以視為驗證通過。
4. **Progressive disclosure** — `SKILL.md` 為進入點，`references/` 僅在需要時才載入，以降低 token 使用量。

語言與行文規範：

- 所有 skill 內容一律以**繁體中文（台灣用語，`zh-TW`）**撰寫，專有名詞（框架、工具、API、指令、檔案路徑）保留原文。
- 維持技術文件的專業語氣：不用句尾語氣詞、不用網路用語、不用 emoji。
