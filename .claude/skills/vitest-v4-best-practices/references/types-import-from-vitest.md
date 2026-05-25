---
rule: types-import-from-vitest
category: 型別測試
tags: [types, Mock, import, jest-namespace]
---

# Mock 等型別從 `vitest` import

> Vitest 沒有全域的 `jest` namespace。`Mock`、`Mocked`、`MockInstance` 等型別要從 `vitest` 具名 import，不要寫 `jest.Mock`。

## 原因

- `jest.Mock` 這類全域 namespace 在 Vitest 不存在，沿用會是型別錯誤
- 具名 import 讓型別來源明確，也利於 tree-shaking 與 IDE 跳轉
- 從 Jest 遷移時，型別引用是最常被漏掉、最容易殘留舊寫法的部分

## ❌ Bad

```ts
let handler: jest.Mock<(name: string) => number>

const service: jest.Mocked<UserService> = createMock()
```

## ✅ Good

```ts
import type { Mock, Mocked } from 'vitest'

let handler: Mock<(name: string) => number>

const service: Mocked<UserService> = createMock()
```

`vi.fn()` 的回傳型別也可直接用 `Mock`，需要包整個物件的 mock 型別時用 `Mocked<T>`。
