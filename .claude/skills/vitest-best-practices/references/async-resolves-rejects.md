---
rule: async-resolves-rejects
category: 非同步斷言
tags: [async, resolves, rejects, promise, expect]
---

# 非同步斷言用 `await expect(...).resolves` / `.rejects`

> 驗證 Promise 結果或拒絕時，用 `await expect(promise).resolves` / `.rejects`，不要自己 try/catch 再斷言。後者一旦 Promise 沒如預期拒絕，測試會悄悄通過。

## 原因

- 手寫 try/catch 漏掉「沒丟錯」的情況時，測試不會失敗，等於沒測到
- `.rejects.toThrow()` 會在 Promise 未拒絕時主動讓測試失敗，意圖明確
- 整個斷言前加 `await`，確保 Vitest 等到 Promise settle 才判定

## ❌ Bad

```ts
test('rejects invalid input', async () => {
  try {
    await validate(badInput)
    // 若沒丟錯，這裡什麼都不做，測試照樣通過
  } catch (error) {
    expect(String(error)).toContain('invalid')
  }
})
```

## ✅ Good

```ts
test('rejects invalid input', async () => {
  await expect(validate(badInput)).rejects.toThrow('invalid')
})

test('resolves to user', async () => {
  await expect(fetchUser('1')).resolves.toEqual({ id: '1', name: 'Ann' })
})
```

`expect(await fn())` 也可行，但 `.resolves` / `.rejects` 在語意與錯誤定位上更清楚，拒絕情境尤其建議用 `.rejects`。
