---
rule: control-flow-parallel-promises
category: control-flow
tags: [control-flow, async, performance]
---

# 獨立非同步操作用 `Promise.all` 或 `Promise.allSettled`

> 多個互不相依的 async 操作必須 `Promise.all` 平行執行，禁止連續 `await` 造成不必要的等待。

## 原因

- 連續 `await` 是序列執行，總時間等於各操作時間相加
- `Promise.all` 平行執行，總時間等於最慢那個操作的時間
- 對 I/O bound 的 API 呼叫，平行化通常省一個量級的時間

## ❌ Bad

```ts
async function loadDashboard(userId: string) {
  const user = await fetchUser(userId);          // 200ms
  const posts = await fetchPosts(userId);        // 300ms
  const notifications = await fetchNotifications(userId); // 150ms
  // 三者互不相依，卻花了 650ms

  return { user, posts, notifications };
}
```

三個 API 沒有依賴關係，依序 `await` 純粹浪費時間。

## ✅ Good

```ts
async function loadDashboard(userId: string) {
  const [user, posts, notifications] = await Promise.all([
    fetchUser(userId),
    fetchPosts(userId),
    fetchNotifications(userId),
  ]);
  // 總時間約 300ms（取最慢的）

  return { user, posts, notifications };
}

// 部分失敗仍要繼續，改用 Promise.allSettled
async function loadWidgets(widgetIds: string[]) {
  const results = await Promise.allSettled(
    widgetIds.map(id => fetchWidget(id)),
  );

  return results
    .filter(
      (result): result is PromiseFulfilledResult<Widget> =>
        result.status === 'fulfilled',
    )
    .map(result => result.value);
}
```

互不相依的呼叫一次發出，整體延遲取決於最慢的一個。需要容錯時改 `Promise.allSettled`。

## 例外

- 後一步需要前一步的結果（例如先 `fetchUser` 拿到 `companyId` 才能 `fetchCompany`），就必須序列
