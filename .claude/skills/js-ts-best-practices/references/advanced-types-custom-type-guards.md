---
rule: advanced-types-custom-type-guards
category: advanced-types
tags: [advanced-types, type-guard, narrowing]
---

# 自訂 type guard 封裝重複收窄

> 重複出現的型別收窄邏輯，用自訂 type guard（`function isX(value): value is X`）封裝，呼叫端用一個函式就完成收窄。

## 原因

- 把判斷邏輯集中在 type guard 內，呼叫端不需要散落 `typeof` + `in` 的組合
- 收窄結果型別由 `value is X` 明示，TS 後續會自動收窄，不必再用 `as`
- 把「runtime 檢查」與「靜態型別」綁在一起，兩者同步演進

## ❌ Bad

```ts
type User = { id: string; name: string };

function process(data: unknown) {
  if (
    typeof data === 'object' &&
    data !== null &&
    'id' in data &&
    'name' in data
  ) {
    console.log((data as User).id);
  }
}

function processAgain(data: unknown) {
  if (
    typeof data === 'object' &&
    data !== null &&
    'id' in data &&
    'name' in data
  ) {
    console.log((data as User).name);
  }
}
```

同樣的判斷邏輯散落兩處，又得在收窄後手動 `as User` 補回型別，重複又脆弱。

## ✅ Good

```ts
type User = { id: string; name: string };

function isUser(data: unknown): data is User {
  return (
    typeof data === 'object' &&
    data !== null &&
    'id' in data &&
    'name' in data &&
    typeof (data as Record<string, unknown>).id === 'string' &&
    typeof (data as Record<string, unknown>).name === 'string'
  );
}

function process(data: unknown) {
  if (isUser(data)) {
    console.log(data.id); // 已收窄為 User
  }
}
```

`isUser` 同時是 runtime 檢查與型別收窄的單一來源，呼叫端直接用 `if (isUser(...))` 即可。

## 例外

- 一次性、邏輯極簡的收窄（例如 `typeof x === 'string'`），直接內聯反而清楚
