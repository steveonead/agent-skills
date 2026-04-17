# Ticket Templates

本檔提供 `prd-to-tickets` skill 建立 GitHub issues 時使用的 vertical slice body 模板。**不要**直接複製模板到 issue，先依該 slice 的實際內容填空與裁剪。

---

## Vertical Slice Template

用於 slice issue（title 形如 `<prd-number>.<slice-num> <標題>`，例如 `42.1 專案骨架與 Docker Compose`，label 含 `Type:AFK` 或 `Type:HITL`）。描述端到端行為與驗收，**不分層列實作細節**（讓認領的全端工程師自己決定怎麼切實作步驟）。

> Issue 之間的 blocking 關係以 GitHub 原生 Dependencies 建立（見 SKILL.md 步驟 7 與 `github-api-workflow.md`），不在 body 重複列出。

### 禁止在 body 參照其他 slice 的編號

草擬 body 時，其他 slice 的 GitHub issue number 還不存在（issue 尚未建立），容易誤寫成 slice title 前綴（如 `85.3 接手`、`85.5 負責`）。這種寫法：

- 不會在 GitHub UI 形成 auto-link（只有 `#N` 才會）
- 建票後也不會被回頭替換，變成純文字會隨 scope 調整 rot
- 與 Dependencies API 表達的關聯重複，狀態一不同步就誤導讀者

規則：

1. **body 內不得出現 `<prd-number>.<slice-num>` 或硬編的 `#N` 來指向其他 slice**（對應的 issue 根本還沒建立，無從取得正確編號）
2. 若需表達「本 slice 不含 X」，只寫「由另一張 slice 負責」或「不在本 slice 範圍」等無指向語句；實際關聯由 Dependencies UI 呈現
3. 需要表達 scope 切分時，用 PRD 的 user story 編號（如 `User story 14`）描述範圍，這是 PRD 的穩定 ID，不是 slice 的臨時編號
4. 指向 parent PRD issue 的 `#<prd-number>` 例外允許（步驟 7 建票當下就存在，不會 404）

```markdown
## 對應 PRD

#<prd-issue-number>

## 端到端行為

以一段話描述這個 slice 完成後，使用者可以做到什麼。從使用者的視角出發，不提 FE/BE/DB。

## Demo 驗收情境

完成此 slice 後，應能 demo 以下情境：

- [ ] [可展示的情境 1]
- [ ] [可展示的情境 2]

## 涵蓋的 User Stories

引用 PRD 中的編號：

- User story 3（一句話簡述內容）
- User story 7（一句話簡述內容）

## 實作提示（選填）

若有需要提示認領者的關鍵決策、易踩的雷、或建議的測試切入點，寫在這裡。沒有就刪掉本段。

## 備註

任何不在 slice scope 內但相關的功能、後續可能的 follow-up、或其他特殊考量。沒有就刪掉本段。
```
