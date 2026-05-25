---
rule: router-deferred-loading
category: Router 路由與導航
tags: [router, loader, suspense, prefetch, deferred]
---

# 關鍵資料 `await`、非關鍵不 await + `<Suspense>`

> Loader 內把資料分成「關鍵」與「非關鍵」兩類：關鍵資料用 `await ensureQueryData` 阻塞導航直到完成；非關鍵資料用 `prefetchQuery`（不 await），元件端用 `useSuspenseQuery` + `<Suspense>` 串流呈現。

## 原因

- 將所有資料一律 `await` 會使導航時間延長至最慢的 request 完成為止，明顯影響使用者體感
- 非關鍵資料（推薦、留言、相關文章）不應阻塞主內容的呈現
- `prefetchQuery` 不 await 即為背景發起 request，元件 mount 後由 `useSuspenseQuery` 接手等待，搭配 `<Suspense>` 提供細粒度的 loading UI
- Router 的 `pendingComponent` 對應「整個 route 仍在 loading」；`<Suspense>` 對應「特定區塊仍在 loading」，職責劃分清楚

## ❌ Bad

```ts
// 全部 await —— 留言載入較慢時，主文章也會被阻塞
export const Route = createFileRoute("/posts/$postId")({
  loader: async ({ context, params }) => {
    await context.queryClient.ensureQueryData(postQueryOptions(params.postId));
    await context.queryClient.ensureQueryData(commentsQueryOptions(params.postId));
    await context.queryClient.ensureQueryData(relatedQueryOptions(params.postId));
  },
  component: PostPage,
});
```

## ✅ Good

```ts
export const Route = createFileRoute("/posts/$postId")({
  loader: ({ context, params }) => {
    // 非關鍵資料 —— 背景啟動，不 await
    context.queryClient.prefetchQuery(commentsQueryOptions(params.postId));
    context.queryClient.prefetchQuery(relatedQueryOptions(params.postId));

    // 關鍵資料 —— await 完成後才呈現頁面
    return context.queryClient.ensureQueryData(postQueryOptions(params.postId));
  },
  component: PostPage,
});

function PostPage() {
  const { postId } = Route.useParams();
  const { data: post } = useSuspenseQuery(postQueryOptions(postId));

  return (
    <>
      <PostContent data={post} />
      <Suspense fallback={<CommentsSkeleton />}>
        <Comments postId={postId} />
      </Suspense>
      <Suspense fallback={<RelatedSkeleton />}>
        <Related postId={postId} />
      </Suspense>
    </>
  );
}

function Comments({ postId }: { postId: string }) {
  const { data } = useSuspenseQuery(commentsQueryOptions(postId));
  return <CommentList data={data} />;
}
```

| 情境 | loader 做法 | 元件外是否需 `<Suspense>` |
| --- | --- | --- |
| 關鍵資料 | `await ensureQueryData(...)` | 不需要（loader 已 await，cache 命中）|
| 非關鍵資料 | `prefetchQuery(...)`（不 await）| **需要**（資料可能仍在載入中）|

## 例外

簡單頁面（僅有單一資源、無可分離的次要內容）直接 `await ensureQueryData` 即可，無需特別拆分。
