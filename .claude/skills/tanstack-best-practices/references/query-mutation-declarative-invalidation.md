---
rule: query-mutation-declarative-invalidation
category: Query 資料管理
tags: [query, mutation, invalidation, mutationCache, meta]
---

# 用 `MutationCache` + `meta.invalidates` 集中宣告 invalidation

> Mutation 應在 `meta.invalidates` 宣告要 invalidate 的 query keys，由 `MutationCache` 的全域 `onSuccess` callback 統一執行 `invalidateQueries`。比對用 `matchQuery` 做 partial key 模糊比對。透過 `Register` interface 對 `mutationMeta` 做型別化。

## 原因

- 每個 mutation 自行撰寫 `onSuccess: () => invalidate(...)` 容易遺漏，且修改 query key 結構時須逐一搜尋
- 集中於 `MutationCache` 處理可確保所有 mutation 套用一致的 invalidation 邏輯
- `meta.invalidates` 為宣告式寫法：mutation 本體聚焦業務邏輯，invalidation 對象清楚可辨
- v5 的 `Register` interface 讓 `meta` 可由 TypeScript 完整型別化，避免拼錯 key

## ❌ Bad

```ts
// 每個 mutation 各自處理 invalidation —— 容易產生重複，且容易遺漏部分 key
const updateUser = useMutation({
  mutationFn,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ["users"] });
    queryClient.invalidateQueries({ queryKey: ["dashboard", "stats"] });
  },
});

const deleteUser = useMutation({
  mutationFn,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ["users"] });
    // 遺漏 dashboard stats 的 invalidate
  },
});
```

## ✅ Good

```ts
// types/react-query.d.ts —— 型別化 mutation meta
import "@tanstack/react-query";

declare module "@tanstack/react-query" {
  interface Register {
    mutationMeta: {
      invalidates?: ReadonlyArray<ReadonlyArray<unknown>>;
    };
  }
}
```

```ts
// app.tsx —— MutationCache 集中處理
import { MutationCache, QueryClient, matchQuery } from "@tanstack/react-query";

const queryClient = new QueryClient({
  mutationCache: new MutationCache({
    onSuccess: (_data, _variables, _context, mutation) => {
      queryClient.invalidateQueries({
        predicate: (query) =>
          mutation.meta?.invalidates?.some((queryKey) =>
            matchQuery({ queryKey }, query),
          ) ?? false,
      });
    },
  }),
});
```

```ts
// 各 mutation 改為宣告式
const updateUser = useMutation({
  mutationFn,
  meta: {
    invalidates: [["users"], ["dashboard", "stats"]],
  },
});

const deleteUser = useMutation({
  mutationFn,
  meta: {
    invalidates: [["users"], ["dashboard", "stats"]],
  },
});
```

`matchQuery` 會以 `["users"]` 作為 prefix 比對 cache 內所有 query，自動涵蓋 `["users", "list", ...]`、`["users", "detail", id]` 等子 key，毋須逐一列舉。

## 例外

特殊 mutation（如需要 `setQueryData` 做 optimistic update）可以在自己的 `onMutate` / `onError` / `onSuccess` 內處理；全域 `MutationCache.onSuccess` 仍會在最後執行 invalidate，兩者不衝突。
