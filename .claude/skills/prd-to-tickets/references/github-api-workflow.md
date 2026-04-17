# GitHub API Workflow

> 對應 GitHub REST API 版本：`2026-03-10`
> 驗證日期：2026-04-17
> 驗證來源：<https://docs.github.com/en/rest/issues/issue-dependencies>

本檔描述步驟 7「建立 GitHub issues」的具體流程。步驟 7 一律由 sub-agent 執行（見 `subagent-prompt.md`），本檔是 sub-agent 要讀的操作手冊。

執行前，slice 計畫與每張 issue 的 body 全文應已備妥（依 SKILL.md 步驟 4–6 + `references/ticket-templates.md`）。

---

## 1. 建立必要 labels

掃描既有 labels；缺的先建：

```bash
gh label list --json name --jq '.[].name'
```

必要 labels：

| Label | 顏色 | 用途 |
|-------|------|------|
| `Type:HITL` | `F8BBD0`（玫瑰粉） | 需人為決策的 slice |
| `Type:AFK` | `B2DFDB`（薄荷青） | 可獨立推進的 slice |

> `gh label create` 的 `--color` 參數不含 `#`，直接傳六碼 hex。

每張 slice issue 帶恰好一個 `Type:*` label。slice 歸屬由 title 的數字前綴表達（例如 `42.1`、`42.2`），不另設 label。

建立 labels 時可將所有 `gh label create` 呼叫放在**同一個 message** 裡平行送出；彼此無依賴。

---

## 2. 逐 slice 建立 issue

依 slice 編號從小到大建立。**不要**用 `for` 迴圈一次跑完；逐個跑、收下 number、再進下一個，方便失敗時 resume。

```bash
SLICE_NUMBER=$(gh issue create \
  --title "<prd-number>.<slice-num> <slice 標題>" \
  --label "Type:<AFK 或 HITL>" \
  --body "$(cat <<'EOF'
<填入 Vertical Slice Template>
EOF
)" | awk -F/ '{print $NF}')
```

- `<prd-number>` 是 PRD issue 編號（例如 PRD issue 是 `#42`，這裡就寫 `42`）
- `<slice-num>` 從 1 開始累加（或從步驟 6 掃描到的最大編號 + 1 開始）
- `Type:*` 依主 agent 已與使用者確認的 slice 類型帶入
- 範例標題：`42.1 專案骨架與 Docker Compose`

把每個 slice 的 number 收下來，下一步建 dependency 用。

---

## 3. 建立跨 slice dependency（所有 slice 建好後）

GitHub 原生 Issue Dependencies 表達「A is blocked by B」。API 需要 blocker 的**內部 ID**（typed integer，欄位名 `issue_id`，必須用 `-F` 而非 `-f`，否則會被當字串送 → 回 `422 not of type integer`）：

```bash
# 拿 blocker 的內部 id（--jq 限定取 .id，避免整份 JSON 回流）
BLOCKER_ID=$(gh api /repos/:owner/:repo/issues/<blocker_slice_number> --jq '.id')

# 把它設為 <blocked_slice_number> 的 blocker
gh api -X POST /repos/:owner/:repo/issues/<blocked_slice_number>/dependencies/blocked_by \
  -F issue_id=$BLOCKER_ID \
  --jq '.id'
```

刻意放在所有 slice 建好之後：稍後 slice 的 issue 在早期建立當下還不存在，當下建會 404。

**平行化**：多個 dependency 呼叫彼此獨立，**同一 message** 多個 Bash call 平行送出。每個 call 內部仍是 `BLOCKER_ID=$(...) && POST ...` 兩步序列。

> **Fallback**：若 `gh api` 回 `404` 或 `dependencies/blocked_by` 不支援（repo 未啟用），在**被 block 的 issue** body 的 `## 備註` 區塊手動列出 blocker，如 `- Blocked by #102`。不要在 template 預留 `## Blocked by` 段落，避免日後與 GitHub 原生狀態 rot。

---

## API 過期徵兆

若出現下列情況，先確認官方 docs 是否有改動：

- `gh api` 回 `404` 但 repo 明顯有該功能（路徑可能改過）
- 欄位名被拒絕但 payload 看起來正確（可能改名）
- 回傳 schema 與預期不同（response 格式調整）

更新此檔時請同步更新檔頭的「驗證日期」與版本號。
