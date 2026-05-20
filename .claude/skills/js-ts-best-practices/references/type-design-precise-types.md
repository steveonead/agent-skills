---
rule: type-design-precise-types
category: type-design
tags: [type-design, literal-types, template-literal, tuple, branded-type]
---

# 用精確型別取代寬鬆型別

> 用 literal union、template literal、tuple、branded type 取代 `string`、`number`、`any[]` 這類寬鬆型別。型別愈精確，編譯期能擋下的錯誤愈多。

## 原因

- 寬鬆型別等同關閉型別檢查，例如 `status: string` 任何字串都能傳，違反原本意圖
- 精確型別讓 IDE 自動補全與重構更準確
- 不同語意但型別相同的值（`UserId` vs `OrderId`）能在編譯期被區分

## ❌ Bad

```ts
function checkStatus(status: string) {
  // 任何字串都能傳，'pendng' 的拼錯也不會被擋下
}

type Coordinate = number[];
// 長度沒限制，[1] 或 [1, 2, 3, 4] 都合法，也分不出哪個是 x、哪個是 y

function fetchUser(id: string) {}
function fetchOrder(id: string) {}
fetchUser(orderId); // 兩者都是 string，傳錯也不會錯
```

## ✅ Good

```ts
// Literal union — 限定合法值
type Status = 'pending' | 'error' | 'success';
function checkStatus(status: Status) {}

// Template literal — 約束字串格式
type EventName = `on${Capitalize<string>}`;
type CssLength = `${number}px` | `${number}rem` | `${number}%`;

// Tuple — 固定長度與語意
type Coordinate = [x: number, y: number];
type ApiResponse<T> = [data: T, error: null] | [data: null, error: Error];

// Branded types — 區分語意相同的型別
type UserId = string & { readonly __brand: 'UserId' };
type OrderId = string & { readonly __brand: 'OrderId' };

function fetchUser(id: UserId) {}
// fetchUser(orderId) → 編譯錯誤
```

每種精確型別都把原本「會出錯但編譯器看不到」的情境變成編譯期錯誤。
