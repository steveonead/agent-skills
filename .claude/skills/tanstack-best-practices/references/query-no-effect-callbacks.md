---
rule: query-no-effect-callbacks
category: Query 資料管理
tags: [query, v5, migration, side-effect]
---

# `useQuery` 不要寫 `onSuccess` / `onError` / `onSettled`

> v5 已從 `useQuery` 移除 `onSuccess` / `onError` / `onSettled` 三個 callback。副作用（toast、log、navigate 等）必須改放在 `useEffect`、`useMutation` 或 `QueryCache` 的全域 callback 中。

## 原因

- v4 的 callback 會在每次 background refetch 時觸發，導致 toast 重複顯示、log 重複寫入、navigate 重複呼叫
- v5 移除這三個 callback 為 breaking change，舊 codebase 升級時常於此處出錯
- 副作用應與 component lifecycle 綁定（`useEffect`），或在錯誤層級集中處理（`QueryCache` 的全域 `onError`）

## ❌ Bad

```tsx
// v5 中以下寫法會 TypeScript 報錯
const { data } = useQuery({
  ...userDetailOptions(id),
  onSuccess: (user) => {
    toast.success(`Loaded ${user.name}`); // background refetch 亦會觸發顯示
  },
  onError: (error) => {
    logToSentry(error);
  },
});
```

## ✅ Good

```tsx
// 元件層級副作用 —— useEffect 綁 data 變化
function UserProfile({ id }: { id: string }) {
  const { data } = useSuspenseQuery(userDetailOptions(id));

  useEffect(() => {
    analytics.track("user_viewed", { id: data.id });
  }, [data.id]);

  return <Profile user={data} />;
}

// 全域 error logging —— QueryCache callback
const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onError: (error, query) => {
      logToSentry(error, { queryKey: query.queryKey });
    },
  }),
});

// Mutation 的 callback 仍保留，副作用放這裡
const mutation = useMutation({
  mutationFn: updateUser,
  onSuccess: () => toast.success("Updated"),
  onError: (error) => toast.error(error.message),
});
```

## 例外

無。`useQuery` 的這三個 callback 在 v5 已完全移除，不存在合法使用情境。
