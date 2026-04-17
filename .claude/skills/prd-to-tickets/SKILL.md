---
name: prd-to-tickets
description: |
  將 PRD 拆成可獨立認領的 GitHub issues，採用 tracer bullet vertical slice，每個 slice 一張 ticket。
  適用於以下情況：使用者想把 PRD 變成可執行工單、建立 GitHub issues、拆解需求成開發任務、開工前拆 ticket、將 PRD 轉成實作計畫。當使用者提到「拆票」、「PRD 拆 issue」、「建立 ticket」、「拆任務」、「拆 slice」時務必觸發，即使沒明說「GitHub」也先用此 skill。進入前提：PRD 已存在於 GitHub issue；若只有想法或模糊需求，先用 `roast-engineer` / `idea-to-prd` 收斂。
---

# PRD to Tickets

## 概述

將 PRD 拆成 GitHub issues。核心哲學是 **tracer bullet vertical slice**：每個 slice 都是一條橫跨所有整合層（schema、API、UI、tests）的垂直切片，完成後可獨立 demo。**一個 slice 對應一張 ticket**，由單一工程師端到端認領。

---

## 執行流程

### 步驟 1：前置確認

- [ ] 使用者已提供 PRD 的 GitHub issue 編號或 URL
- [ ] `gh auth status` 通過（若未登入，立即停止並告知使用者）
- [ ] 目前 repo 確實是 GitHub remote（非 GitLab、非本地）

若不符合，立即停止並告知使用者：「缺少 [X]，無法繼續。」

---

### 步驟 2：讀取 PRD

若 PRD 不在 context 內，執行：

```bash
gh issue view <number> --comments
```

把 PRD 的 user stories、scope、非目標看完再動手。不要只看標題就猜。

一次讀完後把 user stories 編號 + 摘要留在 context，後續不要再 `gh issue view` 同一張 PRD（會讓長文反覆佔 context）。

---

### 步驟 3：探索 Codebase（選填）

若尚未理解當前程式碼結構，用另一個 Agent 探索現狀（避免污染主 context）。重點關注：

- 既有模組邊界與目錄慣例
- 測試策略與 CI 流程
- 現有的資料模型與 API 風格

這些會影響 slice 拆分的粒度與順序。

---

### 步驟 4：草擬 Vertical Slices

把 PRD 切成 **tracer bullet slices**。每個 slice 是一條端到端窄切片，完成後可 demo，由一位全端工程師獨立完成。

<vertical-slice-rules>
- 每個 slice 跨越所有整合層（schema、API、UI、tests）
- 完成的 slice 可以**獨立 demo 或驗證**
- **多個薄 slice 優於少數厚 slice**
- slice 有 HITL（需人為決策）與 AFK（可自動完成）之分，優先選 AFK
- 一個 slice = 一張 ticket，不再拆成 FE/BE/contract/integration 子票
</vertical-slice-rules>

---

### 步驟 5：與使用者 Quiz

把草案以**編號列表**呈現。每個 slice 顯示：

- **Slice 標題**：簡短描述
- **類型**：HITL / AFK
- **Blocked by**：依賴的其他 slice（若有）
- **涵蓋的 user stories**：對應 PRD 中的編號
- **端到端行為**：一句話描述完成後使用者能做到什麼

向使用者確認：

1. 粒度對嗎？（太粗 / 太細）
2. 依賴關係對嗎？
3. 是否有 slice 該合併或再切？
4. HITL / AFK 標記正確嗎？
5. 每個 slice 是否真的可以**獨立 demo**？若不行，代表不是 vertical slice，要重切。

反覆迭代到使用者點頭。

---

### 步驟 6：守門檢查（必須全通過才能進下一步）

在真正呼叫 `gh issue create` 之前，對**整份草案**逐一確認：

- [ ] 每個 slice 都有對應的 user stories 引用
- [ ] 每個 slice 完成後可獨立 demo（非半成品、非單層）
- [ ] 依賴關係無環（沒有 A blocked by B、B blocked by A）
- [ ] **slice 編號不衝突**：掃描同一 PRD 既有的 issues（title 開頭為 `<prd-number>.<數字> `，注意後面接空格），新 slice 從最大編號 + 1 開始
- [ ] **body 不含跨 slice 的編號參照**：掃描每張 issue body，不得出現 `<prd-number>.<slice-num>`（如 `85.3 接手`）或硬編的 `#N` 指向其他 slice。指向 parent PRD issue 的 `#<prd-number>` 例外允許。詳見 `references/ticket-templates.md` 的「禁止在 body 參照其他 slice 的編號」

> Slice 之間的 blocking 關係不在 body 寫死，而是在步驟 7 用 GitHub 原生 Issue Dependencies API 建立。本步驟只驗證關係規劃是否正確。

任一項不通過，回步驟 4 修改。

---

### 步驟 7：建立 GitHub Issues

**一律交給 sub-agent 執行**，流程與 prompt 組裝見 `references/subagent-prompt.md`，sub-agent 再依 `references/github-api-workflow.md` 逐 slice 建 issue 與 dependency。

理由：即使 slice 數量不多，每個 `gh issue create` / `gh api` 的 tool result 仍會在主 context 留下 issue URL / 編號等雜訊，主 agent 後續還要回報使用者與處理 follow-up，把這段外包能保住主 context 的品質。Sub-agent 最後只回傳「slice → issue 編號」對應表與 fallback 狀況。

> 若 slice 數量 > 10，先回頭檢視 PRD 是否過大、該拆成多個 PRD，再決定是否進此步驟。

---

### 步驟 8：回報使用者

建立完成後，回報：

- Parent PRD issue 編號
- 所有 slice 的 issue 編號與標題列表
- 跨 slice 的 dependency 關係
- **下一步建議**：哪些 slice 可立即認領（無 blocker 的 AFK slice）

**不要**關閉或改動 parent PRD issue。

---

## 常見藉口與反駁

Agent 傾向於以下理由跳過步驟，但這些理由都不成立：

| 藉口 | 反駁 |
|------|------|
| 「使用者沒要求守門檢查，跳過步驟 6。」 | 守門是預設行為，不需使用者每次指定。跳過會產出無法 demo 的厚 slice 或依賴環，事後重切成本更高。 |
| 「Dependencies API 要多打幾次，直接在 body 寫 `## Blocked by` 就好。」 | 原生 Dependencies 有 UI 區塊、blocker 進度追蹤與雙向連結，body 裡的 markdown 會跟狀態 rot。repo 支援時就用原生的。 |
| 「步驟 7 我主 agent 自己跑就好，slice 才幾個。」 | 步驟 7 一律外包給 sub-agent，不論 slice 多寡。`gh` output 會在主 context 留雜訊，影響後續回報與 follow-up 的品質，沒有例外。 |
| 「這個 slice 其實只是個技術重構，不能 demo 也沒關係。」 | 不能 demo 就不是 vertical slice，會變成「先做 X 才能做 Y」的隱性依賴鏈。重構應該嵌進 vertical slice 內，或拆成可驗證的階段（例如「以新模型重寫某 user flow」可 demo 該 flow 仍正常）。 |
| 「PRD 還沒收斂完，我邊拆邊想就好。」 | PRD 沒定型不應進此 skill，先用 `roast-engineer` / `idea-to-prd` 收斂，避免 ticket 建好後還要大改。 |
| 「body 裡寫『85.3 接手』讓讀者知道範圍由誰接，比 Dependencies UI 清楚。」 | 草擬 body 時 slice 的 issue number 還不存在，無法產出 `#N` auto-link；`85.3` 只是純文字不會 cross-link。建完票後也不會回頭替換，會隨 scope 調整 rot。關聯訊息放 Dependencies UI，body 內如需聲明 out of scope，只寫「由另一張 slice 負責」這類無指向句。 |

---

## 警示紅旗

出現以下跡象時，應立即暫停並重新評估：

- 兩個 slice 互相 `Blocked by` 對方 → 依賴環，重新排列
- slice 無法獨立 demo、或用「先做 A 再做 B」的層級語言描述、或標題出現「重構/整理/優化」這類無 demo 動詞 → 都不是 vertical slice，改嵌進有 demo 的 slice 或重新設計
- slice 數量 > 10 → 考慮是否該 PRD 本身應拆成多個 PRD
- 同一張 slice 同時改超過 3 個獨立模組 → 粒度過粗，再切

---

## 風險控制

執行中若出現想跳過步驟的念頭，或 slice 設計有可疑之處，見 `references/objections-and-redflags.md`。該檔收錄常見藉口的反駁，以及該立即暫停重新評估的警示紅旗。

---

## 驗證要求

「感覺正確」不是完成的依據。完成此技能須提供以下實際證據：

- [ ] 所有 slice issue 均已建立，並貼出 issue 編號清單
- [ ] 若 repo 支援原生 Dependencies API，每個 dependency 關係都實際建立其上，`gh issue view <issue>` 的 Dependencies 區塊正確顯示 blocker；若不支援則走 `github-api-workflow.md` 的 fallback 並在回報中註記
- [ ] 守門檢查（步驟 6）全數通過，且結果有列出給使用者看過
- [ ] PRD parent issue 未被修改或關閉

---

## 參考資料

| 檔案 | 用途 |
|---|---|
| `references/ticket-templates.md` | Vertical slice issue body 模板（主 agent 組 body 時讀） |
| `references/subagent-prompt.md` | 步驟 7 sub-agent 的 prompt 模板與呼叫前 checklist |
| `references/github-api-workflow.md` | 步驟 7 具體的 `gh` / `gh api` 流程、labels、dependencies、fallback |
