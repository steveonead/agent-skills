---
rule: type-safety-readonly
category: type-safety
tags: [type-safety, readonly, immutability]
---

# 用 `Readonly`/`readonly` 在編譯期防修改

> 對「不該被修改」的資料用 `readonly`、`Readonly<T>` 或 `as const` 表達，讓編譯器幫忙守住不可變性。

## 原因

- 明示「這份資料不該被修改」的意圖，閱讀者一眼看出契約
- 函式參數標 `Readonly` 後，函式內部如果不小心 `push`/`sort`/重新賦值都會編譯失敗
- 零 runtime 成本，比 `Object.freeze` 更便宜

## ❌ Bad

```ts
function calculateTotal(items: CartItem[]): number {
  items.sort((a, b) => a.price - b.price); // 偷偷改了原陣列
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

type AppConfig = {
  apiUrl: string;
  maxRetries: number;
};
const config: AppConfig = { apiUrl: '/api', maxRetries: 3 };
config.apiUrl = ''; // 沒有任何警告
```

`items.sort()` 會就地修改傳入的陣列，呼叫端可能完全不知情。

## ✅ Good

```ts
function calculateTotal(items: Readonly<CartItem[]>): number {
  // items.sort(...) → 編譯錯誤
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

type AppConfig = {
  readonly apiUrl: string;
  readonly maxRetries: number;
};
const config: AppConfig = { apiUrl: '/api', maxRetries: 3 };
config.apiUrl = ''; // 編譯錯誤

// 既有型別整份變唯讀
type ReadonlyUser = Readonly<User>;
```

任何試圖修改的程式碼都被擋在編譯期，不會出現「跨檔案的隱形副作用」。
