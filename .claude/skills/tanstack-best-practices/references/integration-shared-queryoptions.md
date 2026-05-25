---
rule: integration-shared-queryoptions
category: Query + Router 整合
tags: [integration, queryOptions, prefetch, loader, useSuspenseQuery]
---

# Link prefetch、loader、component 共用同一份 `queryOptions()`

> 同一筆資料在三個地方被觸及——`<Link>` hover prefetch、route loader 的 `ensureQueryData`、component 的 `useSuspenseQuery`——必須使用同一個 `queryOptions()` 工廠回傳的 options。禁止任何一處手寫 query key 或重新組合 options。

## 原因

- 三處共用同一個 factory，query key、`queryFn`、`staleTime` 完全一致，cache 必定命中
- 一旦某處手寫 key，三層 cache 將出現兩份不同的 entry，hover prefetch 失效、loader 重複 fetch、component 又再次發起請求
- factory 函式的型別會自動推導至三處，重構時僅需修改單一來源即可同步生效

## ❌ Bad

```ts
// queries/user.ts
export function userDetailOptions(id: string) {
  return queryOptions({
    queryKey: ["users", "detail", id] as const,
    queryFn: () => fetchUser(id),
  });
}

// Link 在 component 內手寫 prefetch
function UserLink({ id }: { id: string }) {
  const queryClient = useQueryClient();
  return (
    <Link
      to="/users/$userId"
      params={{ userId: id }}
      onMouseEnter={() => {
        queryClient.prefetchQuery({
          queryKey: ["user", id], // 手寫，跟 factory 不一致
          queryFn: () => fetchUser(id),
        });
      }}
    >
      View
    </Link>
  );
}
```

Hover prefetch 寫入 `["user", id]`，loader / component 訂閱 `["users", "detail", id]`，兩個 entry 完全分離。

## ✅ Good

```ts
// queries/user.ts —— 單一事實來源
import { queryOptions } from "@tanstack/react-query";

export function userDetailOptions(id: string) {
  return queryOptions({
    queryKey: ["users", "detail", id] as const,
    queryFn: ({ signal }) => fetchUser(id, { signal }),
    staleTime: 5 * 60_000,
  });
}
```

```tsx
// component 一處：Link 配 router 自動 preload，無需手動處理
<Link to="/users/$userId" params={{ userId: id }}>
  View User
</Link>;
```

```ts
// route loader
export const Route = createFileRoute("/users/$userId")({
  loader: ({ context, params }) =>
    context.queryClient.ensureQueryData(userDetailOptions(params.userId)),
  component: UserPage,
});
```

```tsx
// component
function UserPage() {
  const { userId } = Route.useParams();
  const { data } = useSuspenseQuery(userDetailOptions(userId));
  return <Profile user={data} />;
}
```

搭配 `router-create-router-config` 設定的 `defaultPreload: "intent"` + `defaultPreloadStaleTime: 0`，router hover preload 會自動呼叫 loader，整個 prefetch / load / mount 三階段都吃同一份 cache。

需要在非 Link 元件（如自訂按鈕）手動 prefetch 時，仍透過 factory：

```tsx
function PrefetchButton({ id }: { id: string }) {
  const queryClient = useQueryClient();
  return (
    <button
      onMouseEnter={() =>
        queryClient.prefetchQuery(userDetailOptions(id))
      }
    >
      Load preview
    </button>
  );
}
```

## 例外

無。所有涉及同一筆資料的位置都應該共用同一個 `queryOptions()` 工廠。
