---
rule: migration-test-options-position
category: Vitest 4 API 強制
tags: [migration, test, describe, options, retry, timeout]
---

# `test` / `describe` 的 options 物件放第 2 參數

> Vitest 4 移除了把 options 物件當第 3 參數的舊寫法。`retry`、`timeout`、`concurrent` 等選項要放在第 2 參數（callback 之前）。純數字的 timeout 仍可當第 3 參數。

## 原因

- v3 同時支援第 2 與第 3 參數傳 options，造成 API 混淆，v4 收斂為單一位置
- options 放在 callback 前，閱讀測試時一眼看到 retry / timeout 設定
- 只有「數字 timeout」這個簡寫保留在第 3 參數，物件形式一律前移

## ❌ Bad

```ts
test('flaky api call', () => {
  // ...
}, { retry: 2 })

describe('suite', () => {
  // ...
}, { concurrent: true })
```

options 物件放在 callback 之後，在 v4 不再被接受。

## ✅ Good

```ts
test('flaky api call', { retry: 2 }, () => {
  // ...
})

describe('suite', { concurrent: true }, () => {
  // ...
})

// 純數字 timeout 仍可放第 3 參數
test('slow case', () => {
  // ...
}, 10_000)
```
