---
rule: immutability-prefer-map-set
category: immutability
tags: [immutability, map, set, performance]
---

# 用 `Map`/`Set` 取代物件/陣列模擬

> 鍵值對應用 `Map`，唯一集合用 `Set`，禁止用物件模擬 Map、用陣列模擬 Set。

## 原因

- `Map.get`/`Set.has` 是 O(1)，而 `Array.find`/`Array.includes` 是 O(n)，資料量稍多就有感差距
- `Map` 鍵可以是物件、函式等任意值；普通物件的鍵會被強制轉成字串
- `Set` 自帶去重語意，省去 `includes` + `push` 的樣板程式碼

## ❌ Bad

```ts
// 物件模擬 Map：鍵被字串化，且可能踩到 prototype 屬性
const userScores: Record<string, number> = {};
userScores['alice'] = 95;

// orders × users 是 O(n²)
function attachUsers(orders: Order[], users: User[]) {
  return orders.map(order => ({
    ...order,
    user: users.find(user => user.id === order.userId),
  }));
}

// 陣列模擬 Set：每次新增都得 O(n) 檢查
const uniqueTags: string[] = [];
if (!uniqueTags.includes('typescript')) {
  uniqueTags.push('typescript');
}
```

`orders.map(... users.find ...)` 是 O(n²)，幾千筆資料就會出現明顯的效能瓶頸。

## ✅ Good

```ts
// 鍵值對應用 Map
const userScoreMap = new Map<string, number>();
userScoreMap.set('alice', 95);
userScoreMap.set('bob', 87);

// 先建一次 Map，後續每筆 O(1)
function attachUsers(orders: Order[], users: User[]) {
  const userById = new Map(users.map(user => [user.id, user]));
  return orders.map(order => ({
    ...order,
    user: userById.get(order.userId),
  }));
}

// 唯一集合用 Set
const uniqueTags = new Set<string>();
uniqueTags.add('typescript');
uniqueTags.add('typescript'); // 自動去重

// 快速去重
const uniqueIds = [...new Set([1, 2, 2, 3, 3, 3])]; // [1, 2, 3]

// 大量 contains 檢查
const allowedIds = new Set(['a', 'b', 'c']);
items.filter(item => allowedIds.has(item.id));
```

`Map`/`Set` 把資料結構意圖明示出來，效能也更穩定。

## 例外

- 只有少量 key、且要序列化為 JSON 的情境，普通物件仍是合理選擇（`Map` 預設不可被 JSON 序列化）
