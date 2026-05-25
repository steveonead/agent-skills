---
rule: async-await-assertions
category: 非同步斷言
tags: [async, expect.poll, await, auto-retry]
---

# `expect.poll` 必須 `await`

> `expect.poll` 會反覆執行回呼並 auto-retry，直到斷言通過或逾時。它回傳 Promise，忘記 `await` 會讓測試在斷言完成前就結束，retry 失準甚至漏掉失敗。

## 原因

- auto-retry 是非同步行為，沒 `await` 等於只觸發一次、不等結果
- v3 起忘記 await `expect.poll` 會讓測試直接失敗並跳警告，不會靜默通過，但語意上仍應一律 await，確保 retry 真的等到斷言結果
- 需要輪詢的條件（非同步狀態變化、外部資源就緒）正是 `expect.poll` 的用途，沒 await 就失去輪詢意義

## ❌ Bad

```ts
test('server becomes ready', () => {
  const server = createServer()
  expect.poll(() => server.isReady).toBe(true) // 沒 await，retry 無效
})
```

## ✅ Good

```ts
test('server becomes ready', async () => {
  const server = createServer()
  await expect.poll(() => server.isReady, { timeout: 500, interval: 20 }).toBe(true)
})
```

`expect.poll` 不支援 `.resolves` / `.rejects` 與快照類 matcher，回呼要回傳要斷言的值。
