## /ito-verify 執行結果 — <ISO-date>

**狀態**：<pass | partial | fail>

### Coverage 摘要

- 總 AC 數：N
- 已覆蓋：M（含本次新補 K 條）
- Gap 補完並通過：X
- 失敗：Y
- 無法驗證（UI gap 但無可用 MCP）：Z
- Skipped（工程師選擇）：W

### 本次驗證方式統計

- Integration test：<N> 條
  - frontend: <n>
  - backend: <n>
  - shared: <n>
- MCP 互動：<M> 條
- 使用 MCP：<tool-name | 無>

### Bug issue 變動

- Auto-closed（本次通過）：#A, #B
- Reopened（本次再度失敗）：#C
- 新開（新的失敗 AC）：#D, #E
- Orphan 處理（AC 已從 PRD 移除）：#F (closed) / #G (kept open per 工程師選擇)
- AC edited warning：#H（沿用） / AC#N 以新 issue 追蹤 → #I

### Test conventions 使用

<依 packages 依序列出本次執行使用的 runner 與 test_dir，供未來 re-run 參考。若有寫入 `.claude/ito-verify.config.json` 也在此註明。>

- frontend (apps/web) — vitest, apps/web/tests/integration/
- backend (apps/api) — jest, apps/api/tests/integration/
- shared (packages/schema) — vitest, packages/schema/__tests__/

### 失敗 AC 清單

<每條 failed AC 一行，附對應 bug issue。>

- AC#3「[AC text]」→ #D
- AC#7「[AC text]」→ #E

### 下一步

<依狀態給出建議：
- pass：建議進入 /ito-review 或 merge PR
- partial / fail：請依 bug issues 修復後重跑 `/ito-verify #<prd-number>`
>

---

<!-- 本 comment 由 /ito-verify 自動產生，勿手動編輯 Bug issue 變動區塊 -->
