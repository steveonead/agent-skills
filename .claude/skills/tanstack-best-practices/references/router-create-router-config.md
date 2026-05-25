---
rule: router-create-router-config
category: Router 路由與導航
tags: [router, setup, createRouter, context, preload]
---

# `createRouter()` 必設 context、preload intent、preloadStaleTime 0

> 建立 router 時必須：`createRootRouteWithContext` 注入 `queryClient`、`defaultPreload: 'intent'` 啟用 hover 預載、`defaultPreloadStaleTime: 0` 讓 cache staleness 完全由 React Query 控制。

## 原因

- 若未將 `queryClient` 注入 router context，loader 無法取得 `ensureQueryData`，Query + Router 整合將無法運作
- `defaultPreload: 'intent'` 為 router prefetch 的合理預設：使用者 hover / focus 連結時即啟動載入，預載命中率高且頻寬利用率合理
- 若未設定 `defaultPreloadStaleTime: 0`，router 會自行 cache loader 結果，與 React Query 的 cache 同時存在；設為 0 後 router 一律委由 React Query 判斷是否需要 fetch，由 `queryOptions().staleTime` 決定是否實際發送 request

## ❌ Bad

```ts
// 未注入 context，loader 無法取得 queryClient
const router = createRouter({
  routeTree,
});

// 未設定 preload，每次點擊皆需等待 loader 完成
```

```ts
// __root.tsx
export const Route = createRootRoute({  // 應為 createRootRouteWithContext
  component: RootLayout,
});
```

## ✅ Good

```ts
// __root.tsx
import { createRootRouteWithContext, Outlet } from "@tanstack/react-router";
import type { QueryClient } from "@tanstack/react-query";

export const Route = createRootRouteWithContext<{
  queryClient: QueryClient;
}>()({
  component: RootLayout,
});

function RootLayout() {
  return (
    <>
      <Outlet />
      {import.meta.env.DEV && <DevToolsBar />}
    </>
  );
}
```

```ts
// router.ts
import { createRouter } from "@tanstack/react-router";
import { QueryClient } from "@tanstack/react-query";
import { routeTree } from "./routeTree.gen";

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 30_000 } },
});

export const router = createRouter({
  routeTree,
  context: { queryClient },
  defaultPreload: "intent",
  defaultPreloadStaleTime: 0, // 交由 React Query 的 staleTime 決定
});

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}
```

```tsx
// main.tsx
<QueryClientProvider client={queryClient}>
  <RouterProvider router={router} />
</QueryClientProvider>
```

## 例外

純靜態路由（不整合 React Query）可不注入 queryClient；本 skill 預設為整合場景，純靜態路由不在討論範圍。
