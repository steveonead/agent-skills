---
rule: mocking-restore-reset-clear
category: Mock 與 Spy
tags: [mocking, restoreAllMocks, clearAllMocks, resetAllMocks, cleanup]
---

# 分清 clear / reset / restore 語意

> Vitest 4 改了 `vi.restoreAllMocks` 的行為：它只還原 `vi.spyOn` 建立的 spy，automock 不再受影響。清理 mock 時要依目的選對方法，別期待 `restoreAllMocks` 能重置 automock 狀態。

## 原因

- v4 後 `restoreAllMocks` 只負責把 `vi.spyOn` 的 spy 還原成原始實作，automock 不會被它重置
- 三個方法各司其職：`clearAllMocks` 清呼叫紀錄、`resetAllMocks` 連同清掉實作、`restoreAllMocks` 還原 `vi.spyOn`
- 混用會出現「以為清乾淨、實作卻還在」或「spy 沒還原導致跨測試污染」

## ❌ Bad

```ts
// 用 automock 後，期待 restoreAllMocks 把它的回傳重置回原始行為
vi.mock(import('./service'))

afterEach(() => {
  vi.restoreAllMocks() // automock 的狀態不會被它還原
})
```

## ✅ Good

```ts
afterEach(() => {
  // 清掉所有 mock 的呼叫紀錄（最常用，避免跨測試殘留 call count）
  vi.clearAllMocks()
})

// 需要把 vi.spyOn 的 spy 還原成原始實作時，明確呼叫 restore
const spy = vi.spyOn(obj, 'method')
// ...
spy.mockRestore()
```

也可在 config 設定自動清理，省去手寫 `afterEach`：`clearMocks: true` 在每個測試前清掉呼叫紀錄，`restoreMocks: true` 在每個測試前還原所有 `vi.spyOn`。AI 產生的測試常設了 spy 卻忘了還原，導致 mock 洩漏到後續測試，開 `restoreMocks: true` 是最直接的解法。`mockReset` / `resetAllMocks` 會連實作一起清掉，只在確實要重設行為時用。
