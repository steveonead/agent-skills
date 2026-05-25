---
rule: query-mutation-optimistic-flow
category: Query 資料管理
tags: [query, mutation, optimistic, rollback, cancelQueries]
---

# Optimistic update 必須走完整四步流程

> 需要 optimistic UI 時，`useMutation` 必須完整實作：`onMutate` 內先 `cancelQueries` 再 `setQueryData` 並 return 前一份快照、`onError` 用快照 rollback、`onSettled` 觸發 `invalidateQueries`。少一步就會出現資料漂移或競態。

## 原因

- 若未呼叫 `cancelQueries`，進行中的 refetch 完成後會覆蓋 optimistic 更新的值
- 若未 return snapshot，`onError` 無法執行 rollback，使用者會看到實際已失敗的「成功狀態」
- 若未於 `onSettled` 觸發 invalidate，server 與 client 的最終一致性將失去自動保證
- 此四步流程為 TanStack Query 官方推薦的完整契約

## ❌ Bad

```ts
const mutation = useMutation({
  mutationFn: toggleLike,
  onMutate: (postId) => {
    // 僅更新 cache，未執行 cancel 與備份
    queryClient.setQueryData(["post", postId], (previousPost) => ({
      ...previousPost,
      liked: !previousPost.liked,
    }));
  },
  // 缺少 onError —— 失敗時 UI 將持續停留於錯誤狀態
});
```

## ✅ Good

```ts
const mutation = useMutation({
  mutationFn: toggleLike,

  onMutate: async (postId: string) => {
    // 1. 取消所有進行中的相同 query
    await queryClient.cancelQueries({ queryKey: ["post", postId] });

    // 2. 備份現有 cache 內容
    const previousPost = queryClient.getQueryData<Post>(["post", postId]);

    // 3. 樂觀更新
    queryClient.setQueryData<Post>(["post", postId], (previousPost) =>
      previousPost ? { ...previousPost, liked: !previousPost.liked } : previousPost,
    );

    // 4. 回傳 context 供 onError 使用
    return { previousPost };
  },

  onError: (_error, postId, context) => {
    // 5. rollback
    if (context?.previousPost) {
      queryClient.setQueryData(["post", postId], context.previousPost);
    }
  },

  onSettled: (_data, _error, postId) => {
    // 6. 不論成功或失敗皆與 server 同步
    queryClient.invalidateQueries({ queryKey: ["post", postId] });
  },
});
```

搭配 `query-mutation-declarative-invalidation` 時，`onSettled` 可省略 —— `MutationCache` 的全域 `onSuccess` 已負責執行 invalidate。但 `onError` rollback 仍需保留，因為失敗時不會經過全域 `onSuccess`。

## 例外

不需 optimistic 的單純 mutation 直接套用 `query-invalidate-over-setdata` 規則，無需額外實作 `onMutate`。
