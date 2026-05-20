---
rule: naming-no-magic-values
category: naming
tags: [naming, constants, readability]
---

# 消除魔術數字與字串

> 有特定意義或會重複使用的數字、字串抽成具名常數，禁止直接散落在程式碼裡。

## 原因

- 字面值本身無法表達意圖，讀者得從上下文猜為什麼是這個值
- 改參數時得全檔搜尋字面值，容易遺漏或誤改到語意不同但數值相同的地方
- 抽成常數後，可在常數名上承載業務規則（例如 `MAX_RETRY_COUNT`）

## ❌ Bad

```ts
async function fetchWithRetry(url: string) {
  let retries = 0;
  while (retries < 3) {
    try {
      return await fetch(url);
    } catch {
      retries++;
    }
  }
}

setTimeout(callback, 5000);

if (user.role === 'admin') {
  // ...
}
```

`3`、`5000`、`'admin'` 散落各處，每個都得回頭看上下文才知道意思，改值時也容易漏掉。

## ✅ Good

```ts
const MAX_RETRY_COUNT = 3;
const API_TIMEOUT_MS = 5000;
const ROLE = {
  admin: 'admin',
  member: 'member',
} as const;

async function fetchWithRetry(url: string) {
  let retries = 0;
  while (retries < MAX_RETRY_COUNT) {
    try {
      return await fetch(url);
    } catch {
      retries++;
    }
  }
}

setTimeout(callback, API_TIMEOUT_MS);

if (user.role === ROLE.admin) {
  // ...
}
```

常數名表達了值的用途，改參數只需動一處，型別也能由 `as const` 推得更精確。

## 例外

- 真正不具語意的邊界值，例如 `for (let i = 0; i < arr.length; i++)` 的 `0` 與索引比較
- 數學公式裡的固定常數（`Math.PI * 2`）
- 一次性、語意已由上下文點明的值，例如 `array.slice(0, 10)` 取前十筆且該數字只用一次
