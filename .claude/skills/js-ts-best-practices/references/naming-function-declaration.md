---
rule: naming-function-declaration
category: naming
tags: [naming, function, arrow-function]
---

# 具名函式用 `function`，callback 用 arrow

> 模組層級或可重用的具名函式用 `function` 關鍵字宣告，只有 callback、物件方法與一次性匿名函式才用 arrow function。

## 原因

- `function` 關鍵字一眼就能辨識為函式定義，意圖比 `const x = () => {}` 明確
- `function` 有 hoisting，模組內呼叫順序較有彈性
- Arrow function 適合 callback 那種「不具名也可接受」的短邏輯

## ❌ Bad

```ts
// 模組層級具名函式不該用 arrow
const calculateTotal = (items: Item[]) => {
  return items.reduce((sum, item) => sum + item.price, 0);
};

// callback 不該用冗長的 function expression
const doubled = [1, 2, 3].map(function (value) {
  return value * 2;
});
```

把所有東西都寫成 `const xxx = () => {}` 會讓函式跟一般變數混在一起，閱讀時得多一道判斷。

## ✅ Good

```ts
function calculateTotal(items: Item[]) {
  return items.reduce((sum, item) => sum + item.price, 0);
}

const doubled = [1, 2, 3].map(value => value * 2);

const queryKeyMap = {
  list: () => [],
  detail: (id: string) => [id],
  search: (query: string, page: number) => [query, page],
} as const
```

具名函式用 `function`，callback 用 arrow，兩者各司其職，意圖一目瞭然。
