# Sub-agent Prompt 模板

步驟 7 一律交給 sub-agent 執行。理由：每個 `gh issue create` / `gh api` 即使加 `--jq` 過濾，tool result 仍會留下 issue URL / 編號等文字；主 agent 後續還要回報使用者與處理 follow-up，把這段外包能保住主 context 的品質。Sub-agent 自己吸收這些 output，最後只回傳「slice → issue 編號」對應表，量可壓到 1 KB 以內。

## 呼叫前主 agent 要先備好的東西

在主 context 把下列內容組裝好後再呼叫 sub-agent，這樣 sub-agent 不必讀 PRD、不必讀 templates：

- [ ] Repo 的 `owner/repo`
- [ ] PRD issue 編號
- [ ] 已通過守門檢查的 slice 計畫（含每 slice 的標題、HITL/AFK、涵蓋的 user stories、slice 間依賴）
- [ ] 每張 issue 的 body 全文（由 `references/ticket-templates.md` 模板填入實際內容）

## 模板

替換所有 `<...>` 後整段丟給 `general-purpose` agent：

```
任務：依照 <絕對路徑>/.claude/skills/prd-to-tickets/references/github-api-workflow.md 的步驟建立本 PRD 的所有 GitHub issues 與 dependency 關係。

Repo: <owner>/<repo>
PRD issue number: <prd-number>

Slice 計畫（已通過守門檢查）：
<在這裡貼上完整 slice 列表，包含：每個 slice 的標題、HITL/AFK、涵蓋的 user stories、slice 間依賴>

每個 issue body 我已經幫你填好如下（結構對應 <絕對路徑>/.claude/skills/prd-to-tickets/references/ticket-templates.md）：
<在這裡貼上每個 issue 已填好的 body 全文，依 slice 編號排序>

嚴格要求：
- 所有 `gh api` 呼叫加 `--jq` 只取需要欄位（通常是 `.id` 或 `.number`），絕不 dump 整份 JSON
- `gh issue create` 的 URL 輸出用 `awk -F/ '{print $NF}'` 取 number
- 跨 slice dependency 必須在所有 slice 的 issue 建好之後才建（早建會 404）
- 多個獨立 dependency 呼叫放在同一 message 內平行送出

完成後僅回傳：
- 每個 slice 的 issue number 與標題
- 已建立的跨 slice dependency 對應表
- 任何錯誤或走 fallback 的狀況（例如 dependencies API 未支援）

不要回傳 JSON dump、不要回傳 URL 列表，只要上述摘要。
```
