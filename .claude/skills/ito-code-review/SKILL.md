---
name: ito-code-review
description: 對 git diff 跑完整 code review，依五大面向輸出報告，並整合 stack 專屬 best practice 規則。適用於 PR 前的 self-review、想系統性檢查自己或 agent 寫的程式碼時。不適用於 PR review 給別人 feedback 或純架構討論。
---

# ito-code-review

## 概覽

PR 送出前的最後把關，對 git diff 依五大面向執行 review：正確性、可讀性、架構、安全性、效能。各面向同步套用 stack 專屬 best practice 規則，審查結果統一呈現，不重複標記。

## 使用時機

- 要送 PR 前，想先自己 review 一遍
- Agent 生了一堆 code，不確定品質怎樣
- 改完某功能，想確認沒帶出安全或效能問題

**不應使用的情況：** 需要給別人 PR feedback、純架構討論、還沒開始寫 code、只是在規劃。

## 核心流程

### 步驟 1：確認 target branch

詢問使用者：「要跟哪個 branch 比？（預設 main）」

收到後跑：

```bash
git diff <target>...HEAD
```

若 diff 為空，回報「跟 `<target>` 沒有差異，沒東西可以 review」並結束。

### 步驟 2：偵測 Stack

讀取 `docs/best-practices/BEST-PRACTICE-MAP.md`，透過分析 diff 的副檔名與 import 語句，記錄命中的 stack，並立即讀取對應的 best practice 文件，供步驟 3 各面向使用。

命中多個 stack 時全部納入。MAP.md 或 best practice 文件不存在時跳過，不報錯。

### 步驟 2.5：偵測新 Dependency

若 diff 包含 `package.json`、`requirements.txt`、`go.mod`、`Cargo.toml`、`pyproject.toml`、`Gemfile` 等 package manager 檔案的變動，對每個新增的 dependency 逐一確認：

1. **必要性**：現有 stack 能解決嗎？有沒有更輕量的替代？
2. **體積**：bundle 影響有多大？
3. **維護狀態**：近期 commit 頻率、open issues 是否合理？
4. **已知漏洞**：`npm audit` / `pip audit` / `cargo audit` / `bundle audit` 有無回報？
5. **授權**：授權是否與專案相容？

沒有 package manager 檔案變動時，跳過本步驟。

### 步驟 3：執行 Review

先掃 diff 中的測試檔案（`*.test.*`、`*.spec.*`、`__tests__/`）：

- 有測試 → 先讀測試，理解預期行為與 edge case 覆蓋範圍，再看實作
- 沒有測試 → 在正確性面向標記 🟡

確認測試意圖後，再依序執行五大面向。

各面向 review 時，同步套用已載入的 best practice 文件中與該面向相關的規則。發現問題時於 finding 後附上規則來源（如 `[JS/TS 7.1]`）。一個 finding 只歸類到最相關的面向，不重複標記。

**五大面向**依序審查 diff：

#### 正確性

- 邏輯符合預期行為嗎？有沒有跟 spec 或需求對不上的地方？
- 邊界條件顧到了嗎？（null、空陣列、零值、超大值）
- Error path 有處理嗎？不只是 happy path 走得通
- 有沒有 off-by-one、race condition、state 不一致的問題？
- 測試有覆蓋這次的改動嗎？測試在測行為，還是只測實作細節？

#### 可讀性

- 命名夠清楚嗎？`data`、`result`、`temp` 這種沒有上下文的名字要特別注意
- 邏輯好追嗎？巢狀三元運算子、深層 callback 要特別注意
- 有沒有「聰明過頭」的寫法，其實可以更直接？
- 這段 code 能不能更短？一千行能用一百行解決是品質問題
- 新的 abstraction 有必要嗎？同一模式出現三次再抽，不要過早
- 有沒有 dead code 殘留？包括 `_unused` 變數、backward-compat shim、`// removed` 的註解

#### 架構

- 有沒有跟現有 pattern 衝突？若引入新 pattern，理由夠充分嗎？
- 模組邊界清不清楚？有沒有不必要的 coupling？
- 有沒有可以共用但重複寫的邏輯？
- Dependency 方向對不對？有沒有循環依賴？
- 抽象層級適當嗎？沒有過度設計，也沒有全部塞在一起？

#### 安全性

讀取 `references/security-checklist.md`，只跑跟 diff 相關的 section。
例如 diff 沒有動 auth 邏輯就跳過 Authentication section，沒有處理外部輸入就跳過 Input Validation section。

#### 效能

讀取 `references/performance-checklist.md`，只跑跟 diff 相關的 section。
例如 diff 只動了 UI 邏輯就跳過 Backend section，沒有動 list render 就跳過 virtualization 相關項目。

### 步驟 4：輸出報告

```
## Code Review：<branch> → <target>

#### 正確性
🔴 [問題描述] `file.ts:42`
🟡 [問題描述] `file.ts:10`

#### 安全性
🔴 [問題描述] `api/route.ts:88`

#### 可讀性
🟡 [問題描述] [JS/TS 1.3] `component.tsx:15`
```

**嚴重度：**
- 🔴 **Critical**：必修，有 bug、安全漏洞或會讓系統掛掉
- 🟡 **Warning**：建議修，影響可維護性或有潛在風險
- 🔵 **Nit**：風格偏好或微小改善，可直接忽略

沒問題的面向或 stack 直接跳過，不輸出「此面向無問題」之類的廢話。

### 步驟 5：審查結論與後續

有 🔴 Critical 時：

```
🚫 有 Critical 問題需要先處理。要我現在修嗎？
```

沒有 Critical 直接結束，不輸出審查結論。使用者確認要修時，逐一用 Edit tool 修 Critical 問題。

## 常見合理化藉口

| 合理化藉口 | 實際情況 |
|---|---|
| 「diff 看起來沒問題，快速帶過就好」 | 跳過 checklist 容易漏掉不明顯的安全或效能問題 |
| 「best practice 文件不存在，跳過」 | 文件不存在時跳過沒問題，但五大面向不能省 |
| 「沒 Critical 就不用說什麼」 | 正確，審查結論只在有 Critical 時輸出 |
| 「把整份 checklist 跑完比較保險」 | 不相關的項目是雜訊，只跑跟 diff 有關的 section |
| 「best practice 規則跨面向，要在兩個地方都標記」 | 一個 finding 只歸一個最相關的面向，不重複標記 |

## 警訊

- 輸出「此面向無問題」（沒問題就不輸出那個 section）
- 跑了跟 diff 完全無關的 checklist 項目
- 有 Critical 卻沒輸出審查結論
- 沒 Critical 卻輸出 🚫
- 正確性、可讀性、架構三大面向的 checklist 點沒有逐一對照就直接跳過
- diff 有 package manager 檔案變動但跳過步驟 2.5
- 步驟 3 沒先看測試就直接進實作

## 驗證

- [ ] diff 非空才繼續
- [ ] 有 package manager 檔案變動時，新 dependency 已逐一確認五項
- [ ] 步驟 3 先讀測試再看實作（或已標記🟡 無測試）
- [ ] 已載入 best practice 文件，且各面向 review 時已套用相關規則
- [ ] Security 和 performance checklist 只跑跟 diff 相關的 section
- [ ] 正確性、可讀性、架構的每個 checklist 點都有對照過
- [ ] 有 Critical 才輸出審查結論
- [ ] 使用者確認要修時，Edit tool 已實際修改對應行

## 延伸參考

- `references/security-checklist.md`：Security 面向 checklist，步驟 3 審查 security 時讀取
- `references/performance-checklist.md`：Performance 面向 checklist，步驟 3 審查 performance 時讀取
- `docs/best-practices/BEST-PRACTICE-MAP.md`：各 stack best practice 的對照表，步驟 2 偵測到對應 stack 時立即讀取，供各面向 review 時使用
