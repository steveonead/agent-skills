---
rule: fixtures-test-extend
category: Fixture 與測試 Context
tags: [fixtures, test.extend, setup, beforeEach]
---

# 可重用 setup 用 `test.extend` fixture

> 重複的測試前置（建立 mock 資料、初始化 client）用 `test.extend` 定義成 fixture，透過參數注入測試，取代散落各檔的 `beforeEach` 加共用可變變數。fixture 只在被用到時才初始化，且能自動清理。

## 原因

- `beforeEach` 搭配外層 `let` 變數容易跨測試殘留狀態，型別也常變成可空
- fixture 採 lazy 初始化，沒用到的 fixture 不會執行，省去不必要的 setup
- fixture 注入是值傳遞，每個測試拿到獨立實例，天然避免共享污染

## ❌ Bad

```ts
let db: TestDatabase

beforeEach(async () => {
  db = await createTestDatabase()
})

afterEach(async () => {
  await db.close()
})

test('saves user', async () => {
  await db.users.insert({ name: 'Ann' })
  expect(await db.users.count()).toBe(1)
})
```

## ✅ Good

```ts
import { test as base } from 'vitest'

const test = base.extend<{ db: TestDatabase }>({
  db: async ({}, use) => {
    const db = await createTestDatabase()
    await use(db)
    await db.close() // use 之後即為清理
  },
})

test('saves user', async ({ db }) => {
  await db.users.insert({ name: 'Ann' })
  expect(await db.users.count()).toBe(1)
})
```

`use(value)` 之前是 setup、之後是 teardown，不必再寫成對的 `beforeEach` / `afterEach`。
