---
rule: naming-callback-no-abbr
category: naming
tags: [naming, callback, readability]
---

# Callback 參數禁用單字母或縮寫

> Callback 的參數一律給完整且有語意的名稱，禁止 `c`、`x`、`e`、`oi` 這種單字母或縮寫。

## 原因

- 單字母參數需要回頭確認 callback 接的是什麼集合，閱讀成本高
- 鏈式操作（`.filter().map().reduce()`）裡縮寫名稱很容易跟其他變數混淆
- 完整命名能讓 callback 內的邏輯獨立可讀，不靠上下文就能懂

## ❌ Bad

```ts
contactList.map(c => c.name);
orderItems.filter(x => x.price > 100);
users.reduce((a, b) => a + b.age, 0);
events.forEach(e => console.log(e.title));

// 過度縮寫一樣不行
orderItems.filter(oi => oi.price > 100);
```

`c`、`x`、`a`、`b` 完全無法傳達是什麼資料，`e` 還會跟 `Error` 或 `Event` 混淆。

## ✅ Good

```ts
contactList.map(contact => contact.name);
orderItems.filter(orderItem => orderItem.price > 100);
users.reduce((totalAge, user) => totalAge + user.age, 0);
events.forEach(event => console.log(event.title));

// 解構時一樣要用有語意的名稱
entries.map(([key, value]) => `${key}: ${value}`);
```

參數名清楚對應集合元素的語意，閱讀時不需要上下文輔助。
