---
rule: mocking-import-actual
category: Mock 與 Spy
tags: [mocking, importActual, importOriginal, partial-mock]
---

# 部分 mock 用 `vi.importActual` 或 `importOriginal`

> 只想 mock 模組的一部分時，用 factory 的 `importOriginal` 參數取回原始模組再覆寫，或在測試內用 `await vi.importActual()`。不要用 Jest 的 `requireActual`，Vitest 沒有這個 API。

## 原因

- Vitest 走 ESM，沒有 `requireActual`，對應的非同步 API 是 `vi.importActual`
- 部分 mock 保留多數真實行為、只替換需要的函式，比整包 mock 更貼近實際
- factory 的 `importOriginal` 已帶好原始模組，展開後覆寫最直接

## ❌ Bad

```ts
const { cloneDeep } = jest.requireActual('lodash') // Vitest 沒有 requireActual

vi.mock('lodash', () => ({
  cloneDeep,
  debounce: vi.fn(),
}))
```

## ✅ Good

```ts
// 用 factory 的 importOriginal 保留其餘實作
vi.mock(import('lodash'), async (importOriginal) => {
  const actual = await importOriginal()
  return {
    ...actual,
    debounce: vi.fn((callback) => callback),
  }
})

// 或在測試內單獨取原始實作
const { cloneDeep } = await vi.importActual<typeof import('lodash')>('lodash')
```
