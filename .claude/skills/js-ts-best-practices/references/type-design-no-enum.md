---
rule: type-design-no-enum
category: type-design
tags: [type-design, enum, as-const]
---

# 禁用 `enum`，改 `as const`

> TypeScript 的 `enum` 一律禁用，改用 `as const` 物件加 union type 推導。

## 原因

- `enum` 不是 JavaScript 原生語法，編譯後產生 IIFE 與反向對應，徒增 bundle 體積
- 數字 enum 自動遞增、反向對應這些行為都是隱藏陷阱，容易出錯
- `as const` 編譯後就是普通物件，行為一致、零額外成本，型別也能正確推導

## ❌ Bad

```ts
enum Status {
  Fail = -1,
  Success = 1,
  Pending = 0,
}

// 編譯後產生 IIFE 與雙向對應，Status[1] === 'Success' 也合法
```

## ✅ Good

```ts
const STATUS = {
  fail: -1,
  success: 1,
  pending: 0,
} as const;

type Status = (typeof STATUS)[keyof typeof STATUS]; // -1 | 1 | 0

function setStatus(status: Status) {
  // ...
}

setStatus(STATUS.success);
```

`as const` 物件就是普通 JavaScript，型別由 `typeof` 推導出 union，沒有 enum 的副作用。
