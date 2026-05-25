---
rule: router-state-components
category: Router 路由與導航
tags: [router, errorComponent, notFoundComponent, pendingComponent]
---

# Route 必須提供 `errorComponent` / `notFoundComponent` / `pendingComponent`

> 對外公開的 route（非純粹 layout）必須提供：`errorComponent` 處理 loader / beforeLoad throw、`notFoundComponent` 處理 404、`pendingComponent` 處理 loading（或在 router 設 default）。禁止把錯誤丟給沒有 fallback 的最上層 ErrorBoundary。

## 原因

- Loader / beforeLoad 失敗時若未提供 `errorComponent`，整個 app 會 unmount 至最近的 ErrorBoundary，使用者將看到空白頁面或全域錯誤頁
- `notFoundComponent` 為「找不到該筆資源」的情境提供專屬 UI，而非顯示與情境不符的錯誤訊息
- `pendingComponent` 對應「資料載入中」，與 `<Suspense>` 邊界互補：Suspense 處理 component 內部資料，pendingComponent 處理整個 route 切換

## ❌ Bad

```ts
export const Route = createFileRoute("/posts/$postId")({
  loader: ({ context, params }) =>
    context.queryClient.ensureQueryData(postQueryOptions(params.postId)),
  component: PostPage,
  // 沒有錯誤、404、pending 處理
});
```

文章不存在時 `fetchPost` 拋出錯誤 → 整個 app 將 unmount 至全域 ErrorBoundary。

## ✅ Good

```tsx
import {
  createFileRoute,
  ErrorComponentProps,
  notFound,
} from "@tanstack/react-router";

export const Route = createFileRoute("/posts/$postId")({
  loader: async ({ context, params }) => {
    const post = await context.queryClient.ensureQueryData(
      postQueryOptions(params.postId),
    );
    if (!post) throw notFound();
    return post;
  },
  component: PostPage,
  pendingComponent: () => <PostSkeleton />,
  errorComponent: PostErrorBoundary,
  notFoundComponent: () => <PostNotFound />,
});

function PostErrorBoundary({ error, reset }: ErrorComponentProps) {
  return (
    <div role="alert">
      <h2>無法載入文章</h2>
      <pre>{error.message}</pre>
      <button onClick={reset}>重試</button>
    </div>
  );
}
```

或於 `createRouter()` 設定全域 default：

```ts
// 延遲顯示 pendingComponent 的門檻，避免快速回應時的閃爍
const PENDING_DELAY_MS = 500;
// pendingComponent 最少顯示時間，避免閃現後又快速消失
const PENDING_MIN_DISPLAY_MS = 800;

export const router = createRouter({
  routeTree,
  context: { queryClient },
  defaultErrorComponent: GlobalErrorComponent,
  defaultNotFoundComponent: GlobalNotFound,
  defaultPendingComponent: GlobalSpinner,
  defaultPendingMs: PENDING_DELAY_MS,
  defaultPendingMinMs: PENDING_MIN_DISPLAY_MS,
});
```

個別 route 仍可覆寫成更精準的 fallback。

## 例外

純 layout route（只負責 wrap 子 route）通常不需要自己的 pending / error component，由子 route 與全域 default 處理。
