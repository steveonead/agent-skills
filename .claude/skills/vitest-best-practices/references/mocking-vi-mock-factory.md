---
rule: mocking-vi-mock-factory
category: Mock 與 Spy
tags: [mocking, vi.mock, factory, hoisted, default-export]
---

# `vi.mock` 用 `import()` 路徑與 factory

> 用 `vi.mock(import('./module'), factory)` 取得型別安全的路徑。factory 內若要用外部變數，必須透過 `vi.hoisted` 提升，因為 `vi.mock` 會被 hoist 到檔案頂端；mock 預設匯出要回傳 `default` 鍵。

## 原因

- `vi.mock` 在編譯期被提升到所有 import 之前，factory 直接引用外部變數會因尚未初始化而拋出 ReferenceError
- `vi.hoisted` 讓共用的 mock 變數一起被提升，是唯一安全的共享方式
- 傳 `import('./module')` 而非字串，路徑與匯出名稱都能被 TypeScript 檢查

## ❌ Bad

```ts
import { fetchUser } from './userService'

const mockFetch = vi.fn() // factory 提升後此變數還是 undefined

vi.mock('./userService', () => ({
  fetchUser: mockFetch,
}))
```

## ✅ Good

```ts
import { fetchUser } from './userService'

const { mockFetch } = vi.hoisted(() => ({ mockFetch: vi.fn() }))

vi.mock(import('./userService'), () => ({
  fetchUser: mockFetch,
}))

// 有 default export 時，factory 要回傳 default 鍵
vi.mock(import('./logger'), () => ({
  default: { log: vi.fn() },
}))
```

`vi.mock` 的 factory 使用 top-level await，被 mock 的模組無法再用 `require()` 載入。
