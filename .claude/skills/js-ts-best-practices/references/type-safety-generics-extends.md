---
rule: type-safety-generics-extends
category: type-safety
tags: [type-safety, generics, extends]
---

# 泛型用 `extends` 限制範圍

> 函式或型別宣告泛型參數時，必須用 `extends` 限制其形狀，禁止單純 `<T>` 後直接存取屬性，或退而求其次用 `any`。

## 原因

- `extends` 是泛型版的「契約」，清楚告訴讀者這個泛型至少要長什麼樣
- 沒有限制的泛型實際上等於 `unknown`，存取屬性會編譯錯誤，或被迫用 `as` 補回去
- 用 `any` 換取彈性等於丟掉型別保護，呼叫端完全失去靜態檢查

## ❌ Bad

```ts
// any 失去型別保護，回傳型別也是 any
function getId(item: any) {
  return item.id;
}

// 太具體，無法複用
function getUserId(user: { id: number; name: string }) {
  return user.id;
}

// 沒有 extends，無法存取 item.id
function getIdRaw<T>(item: T) {
  return item.id; // ❌ 編譯錯誤
}
```

## ✅ Good

```ts
function getId<T extends { id: number }>(item: T): number {
  return item.id;
}

const user = { id: 1, name: 'Alice' };
const post = { id: 101, title: 'Hello' };

getId(user); // OK
getId(post); // OK
getId({ name: 'Bob' }); // 編譯錯誤：缺少 id

// 多重限制
function pickField<T extends object, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

pickField(user, 'name'); // 推斷為 string
pickField(user, 'role'); // 編譯錯誤：user 沒有 role
```

`extends` 同時表達「最低契約」與「保留呼叫端的精確型別」，比 `any` 安全、比具體型別彈性。
