---
rule: query-invalidate-over-setdata
category: Query 資料管理
tags: [query, mutation, invalidateQueries, setQueryData]
---

# Mutation 後預設用 `invalidateQueries`

> Mutation 成功後一律用 `invalidateQueries` 讓相關 query 自己 refetch，禁止手動 `setQueryData` 維護 cache。例外是 optimistic update —— 必須搭配 `onMutate` + rollback。

## 原因

- 手動 `setQueryData` 需同時維護 list cache、detail cache、pagination cache、infinite cache，只要遺漏其中一處，UI 便會顯示舊資料
- `invalidateQueries` 將一致性問題交回 server 處理，雖多一次 request，但可徹底避免 cache 漂移
- 額外的網路成本通常可忽略，相較之下手動維護帶來的 bug 風險明顯更高

## ❌ Bad

```ts
const mutation = useMutation({
  mutationFn: updateUser,
  onSuccess: (updatedUser) => {
    // 更新了 detail cache
    queryClient.setQueryData(["users", "detail", updatedUser.id], updatedUser);
    // 但遺漏 list cache，列表頁將持續顯示舊資料
  },
});
```

## ✅ Good

```ts
const mutation = useMutation({
  mutationFn: updateUser,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ["users"] });
  },
});
```

對更大範圍的關聯失效，`invalidateQueries` 支援 partial key 模糊比對：

```ts
// 失效所有以 "users" 開頭的 query（含 list、detail、search 等）
queryClient.invalidateQueries({ queryKey: ["users"] });

// 以 predicate 函式進行更精細的控制
queryClient.invalidateQueries({
  predicate: (query) =>
    query.queryKey[0] === "users" && query.queryKey[1] !== "draft",
});
```

## 例外

- **Optimistic update**：需要在 mutation 回傳前更新 UI，搭配 `onMutate` + `onError` rollback 使用 `setQueryData`（見 `query-mutation-optimistic-flow`）
- **WebSocket / SSE 推播**：server 主動推送新資料，可直接 `setQueryData` 寫入；但同時要 `invalidateQueries` 確保跨 client 一致
