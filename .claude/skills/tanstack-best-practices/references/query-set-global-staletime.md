---
rule: query-set-global-staletime
category: Query 資料管理
tags: [query, staleTime, queryClient, defaults]
---

# 全域 `staleTime` 至少設 30 秒

> 建立 `QueryClient` 時必須在 `defaultOptions.queries.staleTime` 設一個合理值（建議至少 30 秒），禁止使用預設值 `0`。需要即時資料的 query 再個別覆寫。

## 原因

- TanStack Query 預設 `staleTime: 0`，意味著每次元件 mount、視窗 focus、網路重連都會觸發 refetch
- 多數應用的資料延遲數十秒可接受，預設 0 會在開發階段產生大量不必要的請求與 UI 閃爍
- 全域設定一個基底值（30 秒），仍在 fresh 期間的 query 直接讀取 cache；需要即時資料的 query 則於 `queryOptions()` 內個別覆寫

## ❌ Bad

```ts
// 預設 staleTime: 0
const queryClient = new QueryClient();

// component 每次重 mount 都 refetch
function Page() {
  const { data } = useQuery(userDetailOptions(id));
}
```

切回 tab、resize、Suspense 切換時，整個資料樹會被完整 refetch 一次。

## ✅ Good

```ts
// app.tsx
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000, // 全域基底：30 秒內視為 fresh
    },
  },
});

// queries/dashboard.ts —— 需要更長的 query 個別覆寫
export function dashboardStatsOptions() {
  return queryOptions({
    queryKey: ["dashboard", "stats"] as const,
    queryFn: fetchDashboardStats,
    staleTime: 5 * 60_000, // 5 分鐘
  });
}

// queries/notifications.ts —— 需要即時資料者則設為 0
export function notificationsOptions() {
  return queryOptions({
    queryKey: ["notifications"] as const,
    queryFn: fetchNotifications,
    staleTime: 0,
    refetchInterval: 10_000,
  });
}
```

## 例外

開發階段想觀察 refetch 行為時，可暫時把 staleTime 拉到 0；上線版本必須有明確的全域基底。
