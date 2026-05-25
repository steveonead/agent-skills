---
rule: query-options-factory
category: Query 資料管理
tags: [query, queryOptions, query-key, dry]
---

# 用 `queryOptions()` 統一管理 Query 定義

> 把 query key、`queryFn`、`staleTime` 等選項打包進一個 `queryOptions()` 工廠函式，讓 component、loader、prefetch 共用同一份定義。禁止在多處重複手寫 query key。

## 原因

- Query key 散落各處在執行 `invalidateQueries` 時容易出錯：少一層、多一層、字串型別不一致皆會導致 invalidation 失敗
- `queryOptions()` 為 v5 新增的型別安全 API，可讓 `getQueryData()`、`prefetchQuery()`、`useQuery()` 共享同一份型別推導
- Component、loader、`<Link>` prefetch 共用同一個 factory，後續修改 staleTime 或 fetch 邏輯僅需異動單一處

## ❌ Bad

```ts
// component 內手寫 query key
function UserProfile({ id }: { id: string }) {
  const { data } = useQuery({
    queryKey: ["users", "detail", id],
    queryFn: () => fetchUser(id),
    staleTime: 5 * 60_000,
  });
}

// loader 又手寫一份，key 結構不同
export const Route = createFileRoute("/users/$userId")({
  loader: ({ context, params }) =>
    context.queryClient.ensureQueryData({
      queryKey: ["user", params.userId], // 少了 "detail" 一層
      queryFn: () => fetchUser(params.userId),
    }),
});
```

Loader 載入的 cache 與 component 訂閱的 key 不一致，導航後 component 仍需重新發出 request。

## ✅ Good

```ts
// queries/user.ts
import { queryOptions } from "@tanstack/react-query";

export function userDetailOptions(id: string) {
  return queryOptions({
    queryKey: ["users", "detail", id] as const,
    queryFn: ({ signal }) => fetchUser(id, { signal }),
    staleTime: 5 * 60_000,
  });
}

// component
const { data } = useSuspenseQuery(userDetailOptions(id));

// loader
context.queryClient.ensureQueryData(userDetailOptions(userId));

// hover prefetch
queryClient.prefetchQuery(userDetailOptions(userId));
```

三處共用 `userDetailOptions(id)`，可確保 key 與 fetch 邏輯完全一致，TypeScript 會從 `queryFn` 自動推導 `data` 型別。

## 例外

複雜的 list / detail / mutation key 體系可額外搭配 query key factory（物件結構），但所有 `useQuery` / `ensureQueryData` 仍透過 `queryOptions()` 函式取用，不直接寫 array literal。
