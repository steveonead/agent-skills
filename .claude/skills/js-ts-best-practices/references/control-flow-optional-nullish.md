---
rule: control-flow-optional-nullish
category: control-flow
tags: [control-flow, optional-chaining, nullish-coalescing]
---

# 用 `?.` 與 `??`，避開 `||` 的 falsy 陷阱

> 存取可能為 null/undefined 的屬性用 `?.`，提供預設值用 `??`，禁止用 `||` 提供預設值。

## 原因

- `||` 對所有 falsy 值（`0`、`''`、`false`、`NaN`）都會 fallback，這幾乎都是 bug，不是設計
- `??` 只對 `null` 與 `undefined` 觸發，正確區分「沒給值」與「給了一個合法 falsy 值」
- `?.` 簡化逐層 null 檢查，意圖比 `a && a.b && a.b.c` 清楚

## ❌ Bad

```ts
// pageSize 為 0 時會錯誤地變成 20
const pageSize = (options && options.pageSize) || 20;

// 使用者把名字設為空字串時會錯誤地變成 'Guest'
const username = (user && user.name) || 'Guest';

// 冗長的逐層檢查
const city = user && user.address && user.address.city;
```

`||` 把合法的 `0` 和 `''` 當作「沒給值」處理，引入難以察覺的邏輯錯誤。

## ✅ Good

```ts
const pageSize = options?.pageSize ?? 20;
const username = user?.name ?? 'Guest';
const city = user?.address?.city;

// 搭配函式呼叫
const result = callback?.();

// 搭配陣列索引
const firstItem = list?.[0];
```

`??` 嚴格區分 nullish 與其他 falsy 值，`?.` 把多層判空收斂成一行。

## 例外

- 當「空字串」「`0`」「`false`」也視為需要 fallback 的條件時，才可以用 `||`，但這種情境應該在程式碼旁註明意圖
