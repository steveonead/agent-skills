---
rule: control-flow-explicit-errors
category: control-flow
tags: [control-flow, error-handling]
---

# 禁止靜默失敗

> 錯誤一律明確處理，要嘛 throw、要嘛回傳明確的失敗結果、要嘛記錄並重拋。空 `catch` 或 `catch (e) {}` 絕對禁止。

## 原因

- 靜默失敗讓 bug 表現成「資料缺漏」「畫面空白」，難以從現象追到根因
- 錯誤處理要在能做出有意義決策的層級，不應該在最底層被默默忽略
- 即使是 fallback 路徑，也該留下足夠的 log 或 metric

## ❌ Bad

```ts
async function fetchUser(id: string) {
  try {
    const response = await fetch(`/api/users/${id}`);
    return await response.json();
  } catch {
    // 什麼都不做
  }
}
```

呼叫端拿到 `undefined` 不知道是「沒這個 user」還是「網路掛了」，後續判斷全錯。

## ✅ Good

```ts
async function fetchUser(id: string): Promise<User> {
  try {
    const response = await fetch(`/api/users/${id}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch user ${id}: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching user:', error);
    throw error;
  }
}
```

呼叫端收到的不是 `User` 就是明確 throw，不會出現「拿到 undefined 卻不知為何」的情況。

## 例外

- 明確規劃成「失敗也要繼續」的容錯場景（例如批次處理、analytics 上報），仍要記錄錯誤，並在註解中說明為何不處理
