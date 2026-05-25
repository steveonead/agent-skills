---
rule: router-loader-ensure-data
category: Router 路由與導航
tags: [router, loader, ensureQueryData, waterfall]
---

# Loader 用 `ensureQueryData` 消除 waterfall

> Route 的 `loader` 必須用 `context.queryClient.ensureQueryData(queryOptions)` 在導航時就開始載資料，禁止等 component mount 後才用 `useQuery` 發請求。Component 內搭配 `useSuspenseQuery` 直接消費 cache。

## 原因

- 等 component mount 才發出 request 會產生 fetch-on-render 的 waterfall，使用者必須等待 JS 載入完成、render 完成後才開始載入資料
- `ensureQueryData` 在 router 解析路由時即執行，與 chunk download 並行進行
- `ensureQueryData` 內部會檢查 cache，已有資料時立即 resolve，不會重複發出 request
- 與 `useSuspenseQuery` 搭配後，component 內 cache 必定命中，實際上不會觸發 suspend

## ❌ Bad

```tsx
export const Route = createFileRoute("/users/$userId")({
  component: UserPage,
});

function UserPage() {
  const { userId } = Route.useParams();
  // 元件 mount 後才 fetch，與 chunk download 形成序列等待
  const { data, isPending } = useQuery(userDetailOptions(userId));
  if (isPending) return <Skeleton />;
  return <Profile user={data} />;
}
```

## ✅ Good

```tsx
import { createFileRoute } from "@tanstack/react-router";
import { useSuspenseQuery } from "@tanstack/react-query";

export const Route = createFileRoute("/users/$userId")({
  loader: ({ context, params }) =>
    context.queryClient.ensureQueryData(userDetailOptions(params.userId)),
  component: UserPage,
});

function UserPage() {
  const { userId } = Route.useParams();
  const { data } = useSuspenseQuery(userDetailOptions(userId));
  return <Profile user={data} />;
}
```

導航時間軸：
- Router 解析路由 → loader 啟動 `ensureQueryData`，同時下載 component chunk
- 兩者並行完成後 → component mount，`useSuspenseQuery` 直接命中 cache，無額外等待

## 例外

非阻塞的次要資料應用 `prefetchQuery` 而非 `ensureQueryData`，見 `router-deferred-loading`。
