---
name: implement-tdd
description: |
  接在 prd-to-tickets 之後，用 TDD red-green-refactor 循環把一張 vertical slice ticket 做到整包測試全綠（不含 commit 與 PR）。
  適用：使用者從 GitHub issue # 出發準備實作新的端到端 behavior。常見說法「開工做 #N」、「實作 #N 的 slice」、「用 TDD 做 #N」、「#N 測試先行」、「認領了 issue #N 從哪開始」、「把 #N 做到全綠」。即使沒明說「TDD」也先觸發。
  不適用：拆 PRD（→ prd-to-tickets）、補測試/補 coverage、純重構任務（沒有新 behavior 要做）、bug fix、設定測試框架、code review、一次性腳本。
  前提：ticket 存在、blocker 已 closed、專案有測試框架——缺一則步驟 1 直接守門。
---

# Implement TDD

## 概述

接在 `prd-to-tickets` 之後：一張 vertical slice ticket 入手，用 TDD 做到整包測試全綠、程式寫完為止。**不 commit、不開 PR、不動 ticket 狀態**，這些交回使用者自己決定。

核心哲學：**測試驗證公開介面的 behavior，不測實作細節**。整份實作換掉、測試仍能通過，才是好測試。

為什麼要 TDD？因為它強迫你一次只解決一個問題：先定義觀察得到的 behavior，再實作剛好夠用的程式。少了這道約束，很容易寫出「測 shape 不測 behavior」的測試——資料結構改一下就壞，功能真的壞掉反而測不到。

---

## 核心反模式：Horizontal Slicing

**禁止先把所有測試寫完，再一次寫完所有實作**。這叫 horizontal slicing——把 RED 解讀成「一次寫全部測試」、GREEN 解讀成「一次寫全部程式」。

會產出**沒用的測試**：

- 實作前就把測試寫死，測的是**想像中**的 behavior，不是實際 behavior
- 容易落入測資料結構與函式簽名這類 **shape**——shape 改一下測試就壞，真正的 bug 反而測不到

**正確做法**：tracer bullet vertical slice。一個測試 → 一段實作 → 再來下一個。每個新測試都回應前一輪學到的東西；因為程式剛寫完，你知道哪些 behavior 真正重要、怎麼驗證才切中要害。

```
錯誤（horizontal）：
  RED:   test1, test2, test3, test4, test5
  GREEN: impl1, impl2, impl3, impl4, impl5

正確（vertical）：
  RED→GREEN: test1→impl1
  RED→GREEN: test2→impl2
  RED→GREEN: test3→impl3
  ...
```

---

## 執行流程

### 步驟 1：前置確認（守門）

- [ ] 使用者已提供 ticket 的 GitHub issue 編號或 URL
- [ ] 需讀 ticket 時 `gh auth status` 通過
- [ ] 該 ticket 的 blocker 全部已 closed（用 `gh api` 查 Issue Dependencies）
- [ ] 專案有可跑的測試框架（見下方偵測流程）

**Blocker 未 closed**：立即停止並告知「#N 的 blocker 尚未完成（#A, #B），先把 blocker 做完再回來」。繞過這道檢查等於把 vertical slice 的前提（可獨立 demo）打破。

**Vertical slice 格式**只警告不拒絕：若 title 不符 `<prd>.<slice>` 格式、或 body 沒有 acceptance criteria，提醒一次後**自動繼續流程**，不等使用者回應。原因：這個 skill 的價值是 TDD 流程本身，不是 ticket 格式警察。

#### 測試框架偵測

依序嘗試：

1. 讀 `package.json` scripts、`Makefile`、`justfile`、`pyproject.toml`、`Cargo.toml`、`go.mod` 等，找 `test` 指令
2. 找不到就問使用者：「沒找到測試指令，請告訴我怎麼跑測試？」
3. 使用者回答沒有測試框架 → 立即停止：「TDD 需要能跑的測試框架，請先建立測試環境再回來。」

不要為了繼續下去而產出「只寫程式不寫測試」的輸出——那等於放棄 TDD，違背這個 skill 存在的理由。

---

### 步驟 2：讀懂 Ticket

把 ticket 完整讀一次（acceptance criteria、user stories、端到端行為），讀完把關鍵點留在 context，不要反覆 `gh issue view` 同一張票浪費 context。

關注三件事：

- **可 demo 的端到端行為**：完成後使用者能做到什麼？
- **Acceptance criteria**：驗收時會被檢查的條件清單
- **範圍邊界**：哪些**不是**這張 slice 的責任

讀完仍對 behavior 有歧義，回頭問使用者，別邊做邊猜。邊做邊猜的代價是整輪 TDD 瞄錯方向。

---

### 步驟 3：Planning（寫程式前的設計）

若使用者目前不在 plan mode，可詢問是否要進入 plan mode 討論設計；使用者同意後再呼叫 `EnterPlanMode`，不要未問自行進入。

寫任何程式或測試之前，先與使用者對齊：

- [ ] 確認這張 slice 需要動到 / 新增哪些 **public interface**
- [ ] 列出要測的 **behaviors**（例如「使用者送出空購物車會收到錯誤」），不是實作步驟
- [ ] 指出 [deep module](references/deep-modules.md) 機會：把複雜度藏在小介面後面
- [ ] 依 [介面設計原則](references/interface-design.md) 評估可測試性
- [ ] **使用者明確回覆 OK** 再動手——「沒反對」不算同意，要收到明確回覆

問使用者：「public interface 應該長什麼樣？哪些 behaviors 最重要？」

**你不能測所有東西**。明確和使用者確認哪些 behavior 最重要，把測試火力集中在關鍵路徑與複雜邏輯，不是每一種可能的 edge case 都寫。

為什麼要 planning？因為沒想清楚介面就開寫，tracer bullet 很容易射偏：第一個測試抓錯入口，整輪迭代都在繞遠路。

---

### 步驟 4：Tracer Bullet（打第一發）

寫**一個**測試，驗證系統的**一個** behavior：

```
RED:   針對第一個 behavior 寫測試 → 測試失敗
GREEN: 寫最小夠用的程式讓它通過 → 測試通過
```

這就是 tracer bullet——證明端到端路徑打通。**挑最能涵蓋主要路徑的 behavior 作為第一發，不是 edge case**。原因：edge case 先打會得到一個還不會運作的主路徑 + 一個滿足特例的路徑，證明不了端到端通順。

#### 每輪檢核

```
[ ] 測試描述的是 behavior，不是實作
[ ] 測試只用 public interface
[ ] 內部重構不會讓測試壞掉
[ ] 實作只寫剛好夠通過這個測試的程式
[ ] 沒有順手加未來才會用到的東西
```

好壞測試對照見 [tests.md](references/tests.md)；要 mock 時先讀 [mocking.md](references/mocking.md)——原則是**只在系統邊界 mock，絕不 mock 自家模組**。

---

### 步驟 5：增量循環

對每一個剩下的 behavior，重複：

```
RED:   寫下一個測試 → 失敗
GREEN: 最小程式讓它通過 → 通過
```

規則：

- 一次一個測試
- 只寫剛好夠通過當下這個測試的程式
- 不預測未來的測試
- 測試聚焦於觀察得到的 behavior

為什麼「一次一個」這麼重要？因為上一段程式剛寫完，腦中對系統的理解是最新的——此時選下一個測試才會切中真正未被涵蓋的行為。一次列五個測試，後面四個都是對著舊模型猜。

---

### 步驟 6：重構

所有測試綠了以後，找 [重構候選](references/refactoring.md)：

- [ ] 去重複
- [ ] 把淺模組加深（把複雜度移到簡單介面後面）
- [ ] 自然地套用 SOLID（不為套而套）
- [ ] 想一下新程式對既有程式揭露了什麼問題
- [ ] 每做一步重構都跑測試

**絕不在 RED 狀態重構**。先讓測試綠，再重構。紅燈時同時改 behavior 與結構，失敗是哪個原因造成的會一團亂。

---

### 步驟 7：驗收收尾

「感覺差不多了」不是完成的依據。宣告完成前須提供以下實際證據：

- [ ] 跑整包測試（不只新增的），貼出**全綠的終端機輸出**
- [ ] 逐條列出 ticket 的 acceptance criteria 對應到哪個測試
- [ ] 無 `skip` / `only` / `xit` / `xdescribe` 殘留
- [ ] 步驟 3 Planning 使用者同意的紀錄在 context 中可追溯

**不 commit、不開 PR、不動 ticket 狀態**——決定權交回使用者。

---

## 常見藉口與反駁

Agent 傾向以下理由跳步驟，但這些理由都不成立：

| 藉口 | 反駁 |
|------|------|
| 「一口氣把所有測試寫完再實作比較有系統。」 | 這是 horizontal slicing。測試會測到你**想像**的 behavior 而不是**實際** behavior；資料結構 shape 改一下就壞，真正的 bug 反而測不到。 |
| 「Mock 內部 collaborator 讓測試跑快一點。」 | 測試會跟實作細節耦合，改個內部函式名就壞。只在系統邊界 mock，絕不 mock 自家模組。 |
| 「RED 的時候順便重構，反正等下要綠。」 | RED 重構會讓失敗原因變模糊：測試是因為新 behavior 沒實作才紅，還是被你重構弄壞的？先 GREEN 再重構。 |
| 「這張 slice 很小，不用 planning。」 | 小 slice 更容易把第一個測試瞄錯方向，整輪繞遠路。Planning 幾分鐘，省下的時間是倍數。 |
| 「使用者沒要求補測試，我先把程式寫完。」 | 這個 skill 的前提就是 TDD。沒測試等於沒完成，步驟 7 會卡住。 |
| 「測試只要跑得過就算通過，不用對 acceptance criteria 打勾。」 | Ticket 的 criteria 是與使用者的契約。步驟 7 要把每條 criteria 對應到測試，否則「完成」的定義是空的。 |
| 「訓練資料裡記得這個 library 的用法，跳過文件確認。」 | 訓練資料可能過時；確認當前版本 API 只要幾秒，不夠賠一輪 bug 修。 |
| 「第一個 tracer bullet 選了一個 edge case，反正遲早要寫。」 | Tracer bullet 的目的是證明**主要路徑**端到端打通。先打 edge case 會得到一個還不會動的主路徑 + 一個特例分支，什麼都沒證明。 |

---

## 警示紅旗

出現以下跡象時立即暫停：

- 測試因為改名或搬動**內部**函式而壞 → 測到實作細節，改走 public interface
- 一輪同時寫超過一個測試
- 測試從未看到 RED 就直接 GREEN → 可能是永遠不會失敗的假測試
- 測試裡出現 mock 自家模組 → 重新設計介面讓依賴從外部注入
- 測試數量暴增但測的都是資料 shape 而非 behavior
- 宣告完成時整包測試**有一部分沒跑**（例如只跑某個檔案）
- 為了綠掉某個測試，在程式碼裡埋測試導向的特例分支

---

## 參考資料

| 檔案 | 用途 | 何時讀 |
|---|---|---|
| `references/tests.md` | 好測試 vs 壞測試對照實例 | 步驟 4–5 寫測試前 |
| `references/mocking.md` | 何時 mock、怎麼 mock、絕不 mock 什麼 | 步驟 4–5 遇到外部依賴時 |
| `references/interface-design.md` | 可測試介面設計三原則 | 步驟 3 Planning、步驟 6 重構 |
| `references/deep-modules.md` | 深模組 vs 淺模組 | 步驟 3 Planning、步驟 6 重構 |
| `references/refactoring.md` | 重構候選清單 | 步驟 6 |
