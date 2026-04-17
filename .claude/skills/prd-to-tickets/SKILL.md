---
name: prd-to-tickets
description: |
  將 PRD 拆成可獨立認領的 GitHub issues，採用 tracer bullet vertical slice 搭配 FE/BE 分層子 issue 的混合結構，專為非 full-stack 團隊設計。
  適用於以下情況：使用者想把 PRD 變成可執行工單、建立 GitHub issues、拆解需求成開發任務、開工前拆 ticket、將 PRD 轉成實作計畫。當使用者提到「拆票」、「PRD 拆 issue」、「建立 ticket」、「拆任務」、「拆 slice」時務必觸發，即使沒明說「GitHub」也先用此 skill。進入前提：PRD 已存在於 GitHub issue；若只有想法或模糊需求，先用 `clarify-requirement` / `write-a-prd` 收斂。
---

# PRD to Tickets

## 概述

將 PRD 拆成 GitHub issues。核心哲學是 **tracer bullet vertical slice**——每個 slice 都要是一條橫跨所有整合層的窄切片，完成後可獨立 demo；但因為目標團隊不是 full-stack，slice 不再是「單一 ticket」，而是由一個 **parent issue** 加上 **FE / BE / contract / integration 子 issue** 組成的群組。這樣既保留 vertical slice 的整合風險前置與可驗證價值，又讓每張實作票可由單一角色獨立推進。

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

---

### 步驟 3：探索 Codebase（選填）

若尚未理解當前程式碼結構，用另一個 Agent 探索現狀（避免污染主 context）。重點關注：

- 現有的 FE/BE 專案邊界（monorepo？分 repo？）
- API 合約載體（OpenAPI？tRPC？手刻 types？）
- 既有測試策略（integration test 跑在哪一側？）

這些會影響「contract ticket」的具體產出形式。

---

### 步驟 4：草擬 Vertical Slices

把 PRD 切成 **tracer bullet slices**。每個 slice 是一條端到端窄刀，完成後可 demo。

<vertical-slice-rules>
- 每個 slice 跨越所有整合層（schema、API、UI、tests）
- 完成的 slice 可以**獨立 demo 或驗證**
- **多個薄 slice 優於少數厚 slice**
- slice 有 HITL（需人為決策）與 AFK（可自動完成）之分，優先選 AFK
</vertical-slice-rules>

對**每個 slice**，再拆成下列子 issue：

| 子 issue 類型 | 用途 | 何時省略 |
|---------------|------|---------|
| `contract` | 定義並凍結 API schema / types / 資料結構 | slice 純 FE 或純 BE 時可省略 |
| `be` | 後端實作（含 integration test） | slice 無後端工作時省略 |
| `fe` | 前端實作（使用 mocked API 開發） | slice 無前端工作時省略 |
| `integration` | 串接 FE ↔ BE 的 E2E 驗證 | slice 只有單側時省略 |

**為什麼這樣拆？** 團隊不是 full-stack，一張 ticket 不能要求一個人做兩層。合約先行讓 FE/BE 可以平行推進（FE mock API、BE 跑 integration test），最後用小張 integration ticket 收斂。這保留了 tracer bullet 的整合風險前置，同時讓每張票可由單一角色獨立認領。

---

### 步驟 5：與使用者 Quiz

把草案以**編號列表**呈現。每個 slice 顯示：

- **Slice 標題**：簡短描述
- **類型**：HITL / AFK
- **Blocked by**：依賴的其他 slice（若有）
- **涵蓋的 user stories**：對應 PRD 中的編號
- **子 issue 計畫**：contract ✅ / be ✅ / fe ✅ / integration ✅（勾選實際會產出的）
- **純單側標記**：若省略 contract，明確註明「純 FE」或「純 BE」並給理由

向使用者確認：

1. 粒度對嗎？（太粗 / 太細）
2. 依賴關係對嗎？
3. 是否有 slice 該合併或再切？
4. HITL / AFK 標記正確嗎？
5. **每個 slice 的子 issue 計畫合理嗎？** 特別是：
   - 省略 contract 的 slice，是否真的純單側？
   - 有沒有 slice 漏了 integration ticket？

反覆迭代到使用者點頭。

---

### 步驟 6：守門檢查（必須全通過才能進下一步）

在真正呼叫 `gh issue create` 之前，對**整份草案**逐一確認：

- [ ] 每個 slice parent 都有對應的 user stories 引用
- [ ] **禁止跨層子 issue**：沒有任何一張子 issue 同時帶 `layer:be` 和 `layer:fe`
- [ ] **合約先行**：若 slice 同時包含 FE+BE，必須有 contract sub-issue，且 FE/BE sub-issue 的 `Blocked by` 指向它
- [ ] **integration 票的血統**：若 slice 有 integration sub-issue，其 `Blocked by` 必須列出同 slice 的 FE + BE
- [ ] **純單側 slice 有明確理由**：若 slice 省略 contract，parent body 必須寫明「此 slice 純 FE / 純 BE，因為 X」
- [ ] **slice 編號不衝突**：掃描現有 `slice-NN` label，新 slice 從未用過的編號開始

任一項不通過，回步驟 4 修改。

---

### 步驟 7：建立 GitHub Issues

**建立順序很重要**：parent → contract → be + fe → integration。這個順序讓「Blocked by」能填進真實的 issue 編號。

#### 7.1 確保必要 labels 存在

掃描既有 labels；缺的先建：

```bash
gh label list --json name --jq '.[].name'
```

必要 labels：

| Label | 顏色建議 | 用途 |
|-------|---------|------|
| `slice` | `#0E8A16` | Parent issue 專用 |
| `slice-NN` | `#C2E0C6` | 分組 ID（每個 slice 一個） |
| `layer:contract` | `#FBCA04` | 合約/schema |
| `layer:be` | `#1D76DB` | 純後端 |
| `layer:fe` | `#D93F0B` | 純前端 |
| `layer:integration` | `#5319E7` | 串接 E2E |
| `type:HITL` | `#B60205` | 需人為決策 |
| `type:AFK` | `#0E8A16` | 可獨立推進 |

#### 7.2 建立 parent issue（每個 slice 一次）

使用 `references/ticket-templates.md` 的 **Parent Slice Template**，以 HEREDOC 傳 body：

```bash
gh issue create \
  --title "[slice] <slice 標題>" \
  --label "slice,slice-01,type:AFK" \
  --body "$(cat <<'EOF'
<填入 Parent Slice Template>
EOF
)"
```

記下回傳的 issue 編號（例如 `#101`）。

#### 7.3 建立 contract sub-issue（若需要）

```bash
gh issue create \
  --title "[slice-01][contract] <描述>" \
  --label "slice-01,layer:contract,type:HITL" \
  --body "..."
```

記下編號（例如 `#102`），並**掛載為 parent 的 sub-issue**（見 7.6）。

#### 7.4 建立 BE / FE sub-issues（可平行）

填入 body 時，若有 contract，在 `Blocked by` 欄位寫 `#102`。

```bash
gh issue create --title "[slice-01][be] ..." --label "slice-01,layer:be,type:AFK" --body "..."
gh issue create --title "[slice-01][fe] ..." --label "slice-01,layer:fe,type:AFK" --body "..."
```

#### 7.5 建立 integration sub-issue（若需要）

`Blocked by` 同時列出同 slice 的 BE + FE 編號。

```bash
gh issue create --title "[slice-01][integration] ..." --label "slice-01,layer:integration,type:AFK" --body "..."
```

#### 7.6 掛載 sub-issue 關聯

GitHub sub-issue API 需要的是 issue 的**內部 ID**（不是 issue number），步驟如下：

```bash
# 拿 sub-issue 的內部 id
SUB_ID=$(gh api /repos/:owner/:repo/issues/<sub_number> --jq '.id')

# 把它掛到 parent 底下
gh api -X POST /repos/:owner/:repo/issues/<parent_number>/sub_issues \
  -f sub_issue_id=$SUB_ID
```

對同 slice 的每個 sub-issue 都做一次。

> 若 `gh api` 回 `404` 或 `sub_issues` 不支援，代表 repo 尚未啟用 sub-issues beta。此時退回：在 parent body 的 task list 中以 `- [ ] #<num>` 形式手動列出所有 sub-issue，GitHub 仍會顯示進度。

---

### 步驟 8：回報使用者

建立完成後，回報：

- Parent PRD issue 編號
- 所有 slice parent 編號與標題列表
- 每個 slice 的 sub-issue 樹狀結構（parent → contract → be/fe → integration）
- **下一步建議**：contract tickets 優先認領並凍結合約

**不要**關閉或改動 parent PRD issue。

---

## 常見藉口與反駁

Agent 傾向於以下理由跳過步驟，但這些理由都不成立：

| 藉口 | 反駁 |
|------|------|
| 「這個 slice 很小，一張 ticket 就好，不拆 FE/BE。」 | 團隊不是 full-stack，一張票不能要求一個人跨層。再小也要拆，不然只有一個人做得了。 |
| 「這個 API 合約很簡單，不用 contract ticket。」 | 合約先行的目的不是「合約很複雜」，而是「讓 FE/BE 能平行開工」。只要有 FE+BE，就要有合約時刻。 |
| 「FE 可以等 BE 做完再開工，不用 mock。」 | 這會讓非 full-stack 團隊的排程互鎖。合約凍結後雙方應能平行，FE 用 mock 就是要破這個鎖。 |
| 「integration ticket 沒什麼工作量，合併進 FE 或 BE 就好。」 | 串接失敗通常不歸任一側單獨負責，獨立 ticket 才能釐清問題歸屬與驗收。 |
| 「使用者沒要求守門檢查，跳過步驟 6。」 | 守門是預設行為，不需使用者每次指定。跳過會產出跨層票，事後要重拆成本更高。 |
| 「gh sub-issues API 要多打幾次，直接寫 task list 就好。」 | sub-issue 有原生進度條和雙向連結，task list 沒有。repo 支援時就用原生的。 |

---

## 警示紅旗

出現以下跡象時，應立即暫停並重新評估：

- 使用者描述的 slice 一張票需要同時改 DB 又改 UI → 粒度過粗，再切
- 兩個 slice 互相 `Blocked by` 對方 → 依賴環，重新排列
- 某個 slice 完成後無法獨立 demo → 不是 vertical slice，重新設計
- 某個 sub-issue 的驗收條件需要依賴另一層才能驗證 → 違反「單層獨立驗證」原則
- slice 數量 > 10 個 → 考慮是否該 PRD 本身應拆成多個 PRD

---

## 驗證要求

「感覺正確」不是完成的依據。完成此技能須提供以下實際證據：

- [ ] 所有 slice parent 與 sub-issues 均已建立，並貼出 issue 編號清單
- [ ] `gh issue view <parent>` 輸出顯示 sub-issues 區塊正確列出所有子 issue（或 task list fallback 已正確呈現）
- [ ] 每個 sub-issue 的 `Blocked by` 引用的是**真實存在的 issue 編號**
- [ ] 守門檢查（步驟 6）全數通過，且結果有列出給使用者看過
- [ ] PRD parent issue 未被修改或關閉

---

## 參考資料

- Issue body 模板：`references/ticket-templates.md`（含 Parent Slice / Contract / BE / FE / Integration 五種模板）
- 上游 skill：`clarify-requirement` → `write-a-prd` → **`prd-to-tickets`（本 skill）**
- 靈感來源：[mattpocock/skills/prd-to-issues](https://github.com/mattpocock/skills/blob/main/prd-to-issues/SKILL.md)（本 skill 在其 tracer bullet 哲學上加入 FE/BE 分層以適應非 full-stack 團隊）
