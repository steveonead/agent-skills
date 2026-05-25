---
rule: advanced-types-assertion-functions
category: advanced-types
tags: [advanced-types, assertion-function, narrowing]
---

# 用 assertion function 取代手寫 throw + 轉型

> 「驗證失敗就拋例外」的場景用 assertion function（`function assertX(value): asserts value is X`），TS 會在後續自動收窄型別。

## 原因

- 比起 `if (!isX(value)) throw ...` 後再用 `value`，assertion function 把驗證與收窄合一
- 呼叫端不必額外做型別 narrowing，TS 自動相信 assertion 之後的型別
- 集中錯誤訊息與檢查邏輯，呼叫端只負責對結果做事

## ❌ Bad

```ts
type User = { id: string; name: string };

function loadUser(data: unknown) {
  if (
    typeof data !== 'object' ||
    data === null ||
    !('id' in data) ||
    !('name' in data)
  ) {
    throw new Error('Invalid user');
  }
  const user = data as User;
  return user.id;
}
```

每次要驗證 user 都得重寫一遍判斷與 `as`，錯誤訊息也散落各處。

## ✅ Good

```ts
type User = { id: string; name: string };

function assertUser(data: unknown): asserts data is User {
  if (
    typeof data !== 'object' ||
    data === null ||
    !('id' in data) ||
    !('name' in data)
  ) {
    throw new Error('Invalid user payload');
  }
}

function loadUser(data: unknown) {
  assertUser(data);
  return data.id; // 已收窄為 User，不需要 as
}
```

`assertUser` 同時負責驗證與收窄，呼叫端讀起來就像「斷言這是 User，繼續執行」。

## 例外

- 驗證邏輯非常複雜、需要回傳結構化錯誤而非 throw 的情境，用 `Result<T, E>` 模式比 assertion function 更合適
