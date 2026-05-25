---
rule: router-loaderdeps-search
category: Router 路由與導航
tags: [router, loader, loaderDeps, search-params, blocker]
---

# 🚨 loader 依賴 search params 必須宣告 `loaderDeps`

> 當 loader 讀取 search params 時，必須透過 `loaderDeps` 將要追蹤的 params 明確宣告，否則 router 不會因 search params 變更而重新執行 loader，將導致分頁、filter、排序持續停留在初始值。

## 原因

- TanStack Router 預設不會將 search params 納入 loader cache key，避免每次 URL 微調都觸發 refetch
- `loaderDeps` 明確告知 router 哪些 search 變更需要重新執行 loader，為 router cache 一致性的關鍵
- 未宣告 `loaderDeps` 時，loader 的 `location` 也不會包含 search params（此為 router 的刻意設計，要求開發者明確宣告依賴）

## ❌ Bad

```ts
export const Route = createFileRoute("/posts")({
  validateSearch: zodValidator(z.object({ page: z.number().default(1) })),
  // 未宣告 loaderDeps，page 將持續為初始值
  loader: ({ context }) => {
    return context.queryClient.ensureQueryData(postListOptions(1));
  },
  component: PostList,
});
```

點擊「下一頁」按鈕後 URL 雖已更新，但 loader 未重新執行，畫面仍停留於第一頁。

## ✅ Good

```ts
export const Route = createFileRoute("/posts")({
  validateSearch: zodValidator(
    z.object({
      page: fallback(z.number(), 1).default(1),
      sort: fallback(z.enum(["newest", "popular"]), "newest").default("newest"),
    }),
  ),
  loaderDeps: ({ search }) => ({ page: search.page, sort: search.sort }),
  loader: ({ context, deps }) =>
    context.queryClient.ensureQueryData(postListOptions(deps)),
  component: PostList,
});
```

只宣告會影響 loader 的 search params，避免不相干的 params（如 `theme`）也觸發重新 fetch。`deps` 物件自動成為 `queryOptions` 的 cache key 一部分，Query 與 Router 雙層 cache 都能正確區分。

## 例外

無。Loader 依賴 search params 時此規則無例外，遺漏將直接導致功能失效。
