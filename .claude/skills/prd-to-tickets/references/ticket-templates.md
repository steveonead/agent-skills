# Ticket Templates

本檔提供 `prd-to-tickets` skill 建立 GitHub issues 時使用的五種 body 模板。**不要**直接複製模板到 issue，先依該 slice 的實際內容填空與裁剪。

---

## 1. Parent Slice Template

用於 `[slice] <標題>` 的 parent issue。描述端到端行為，**不寫層級實作細節**。

```markdown
## Parent PRD

#<prd-issue-number>

## End-to-end behavior

以一段話描述這個 slice 完成後，使用者可以做到什麼。從使用者的視角出發，不提 FE/BE/DB。

## Demo criteria

完成此 slice 後，應能 demo 以下情境：

- [ ] [可展示的情境 1]
- [ ] [可展示的情境 2]

## User stories covered

引用 PRD 中的編號（不重抄內容）：

- User story 3
- User story 7

## Sub-issues plan

- [ ] Contract：#<TBD>（若純單側則註明「純 FE / 純 BE，理由：...」並刪除此項）
- [ ] Backend：#<TBD>
- [ ] Frontend：#<TBD>
- [ ] Integration：#<TBD>（若 slice 只有單側可刪除）

## Blocked by

- 其他 slice 的 parent（若有），例如 `#98`
- 或：None — can start immediately

## Notes

（選填）此 slice 的特殊考量、不在此 slice 涵蓋的相關功能、或需特別注意的事項。
```

---

## 2. Contract Sub-issue Template

用於 `[slice-NN][contract]` sub-issue。目的是**凍結 FE/BE 之間的介面**，讓雙方可平行開工。通常是 HITL。

```markdown
## Parent slice

#<parent-slice-number>

## Blocked by

None — can start immediately（通常 contract 是 slice 內第一張票）

## What to define

明確列出需凍結的合約內容：

- [ ] Endpoint 路徑與 HTTP method
- [ ] Request schema（欄位、型別、驗證規則）
- [ ] Response schema（成功與錯誤）
- [ ] 錯誤碼與訊息慣例
- [ ] 必要的 TypeScript types / OpenAPI / tRPC router 定義（依專案現況）

## Deliverables

- [ ] PR：合約檔案（例如 `packages/api-types/<feature>.ts` 或 `openapi.yaml` 更新）
- [ ] 合約經 FE 與 BE 雙方 reviewer approve

## Acceptance criteria

- [ ] 合約檔案已合併進 main
- [ ] FE 與 BE sub-issue 皆已在 `Blocked by` 引用此 ticket

## Why this is HITL

合約需雙方達成共識，且日後修改會同時影響 FE/BE 進度，因此不建議讓單一 agent 自動決策。
```

---

## 3. Backend Sub-issue Template

用於 `[slice-NN][be]` sub-issue。只描述後端工作，不涉及 UI。

```markdown
## Parent slice

#<parent-slice-number>

## Blocked by

- #<contract-issue-number>（若此 slice 有 contract ticket）
- 或：None — can start immediately（若純 BE slice）

## What to build

描述此 ticket 的後端工作範圍：

- [ ] Endpoint / handler 實作
- [ ] DB schema / migration（若有）
- [ ] Business logic
- [ ] 錯誤處理對應合約定義的錯誤碼

## Acceptance criteria

- [ ] 合約定義的所有 endpoints 都有實作
- [ ] Integration test 覆蓋 happy path 與主要錯誤情境
- [ ] 本地或 staging 可用 curl / httpie 呼叫並得到預期回應

## Out of scope

- 前端任何改動
- 串接 FE 的 E2E 測試（留給 integration ticket）
```

---

## 4. Frontend Sub-issue Template

用於 `[slice-NN][fe]` sub-issue。只描述前端工作，**使用 mock API** 以便平行開發。

```markdown
## Parent slice

#<parent-slice-number>

## Blocked by

- #<contract-issue-number>（若此 slice 有 contract ticket）
- 或：None — can start immediately（若純 FE slice）

## What to build

描述此 ticket 的前端工作範圍：

- [ ] UI component 與 layout
- [ ] 表單驗證（對應合約的 request schema）
- [ ] Loading / error / empty state
- [ ] 對 API 的呼叫以 **mock client** 實作，mock 需符合合約

## Acceptance criteria

- [ ] 畫面在所有 state（loading / success / error / empty）下渲染正確
- [ ] Mock API 回傳對合約定義的各種 response 皆能處理
- [ ] 可在本地跑起來並操作到完整流程（即使 BE 還沒 ready）

## Out of scope

- 實際串接後端（留給 integration ticket，屆時把 mock client 換成真的 client）
- BE 任何改動
```

---

## 5. Integration Sub-issue Template

用於 `[slice-NN][integration]` sub-issue。**只有 FE+BE 都合併後才能開工**。

```markdown
## Parent slice

#<parent-slice-number>

## Blocked by

- #<be-issue-number>
- #<fe-issue-number>

## What to do

- [ ] 將 FE 的 mock client 替換為實際的 API client
- [ ] 驗證端到端 user flow（可手動 QA，或補 E2E 自動化測試）
- [ ] 修正對合約理解落差造成的小問題（欄位命名不一致、時區、邊界值等）

## Acceptance criteria

- [ ] 此 slice 的 parent issue 所列所有 demo criteria 都通過
- [ ] E2E user flow 在 staging 環境可完整跑通

## If contract mismatch found

若發現 FE/BE 對合約理解不一致，**不要**在本 ticket 偷偷改一側。應：

1. 回到 contract ticket（或開 follow-up）釐清與修正
2. 必要時補 FE 或 BE 的 follow-up ticket
3. 本 ticket 在合約修正後再繼續

這是為了維持「合約先行」的紀律，避免跨層 hack。
```
