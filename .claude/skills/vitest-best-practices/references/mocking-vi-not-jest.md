---
rule: mocking-vi-not-jest
category: Mock 與 Spy
tags: [mocking, vi, jest, api, ai-pitfall]
---

# 用 `vi` API，不要用 `jest`

> Vitest 沒有全域 `jest` 物件。mock 與 spy 一律用 `vi.fn` / `vi.mock` / `vi.spyOn`。沿用 `jest.*` 會直接拋出 ReferenceError。這是 AI 生成 Vitest 測試最常見的錯誤，因為模型受大量 Jest 程式碼訓練。

## 原因

- Vitest 的 mock / spy 入口是 `vi`，沒有 `jest` 全域，`jest.fn()` 會拋出 ReferenceError
- API 幾乎一對一對應，照著換即可：`jest.fn`→`vi.fn`、`jest.mock`→`vi.mock`、`jest.spyOn`→`vi.spyOn`、`jest.clearAllMocks`→`vi.clearAllMocks`
- LLM 常把 Jest 寫法帶進 Vitest 測試，產出後務必檢查有沒有殘留的 `jest.*`

## ❌ Bad

```ts
const handler = jest.fn()
jest.mock('./userService')
jest.spyOn(obj, 'method')

afterEach(() => {
  jest.clearAllMocks()
})
```

## ✅ Good

```ts
import { vi } from 'vitest'

const handler = vi.fn()
vi.mock(import('./userService'))
vi.spyOn(obj, 'method')

afterEach(() => {
  vi.clearAllMocks()
})
```

即使在 config 開了 `globals: true`（此時 `vi` 也是全域），從 `vitest` 具名 import `vi` 仍是最不會出錯的寫法。
