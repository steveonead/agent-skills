---
rule: query-suspense-first
category: Query 資料管理
tags: [query, suspense, useSuspenseQuery, error-boundary]
---

# 預設用 `useSuspenseQuery` + Suspense + ErrorBoundary

> 元件內預設使用 `useSuspenseQuery`，loading 與 error 由外層 `<Suspense>` 與 `<ErrorBoundary>` 處理。不要在元件本體寫 `if (isPending) ...` / `if (isError) ...` 分支。

## 原因

- v5 起 `useSuspenseQuery` / `useSuspenseInfiniteQuery` / `useSuspenseQueries` 已成為 first-class API（不再為實驗性質），回傳值 `data` 在型別上不會是 `undefined`
- 於元件本體分支 `isPending` / `isError` 會使元件職責過度擴張，且 TypeScript 必須容忍 `data` 可能為 undefined
- 以 Suspense 邊界統一處理 loading 狀態，搭配 Router 的 `pendingComponent`、`errorComponent` 即可，元件邏輯更加清晰、職責更單純

## ❌ Bad

```tsx
function UserProfile({ id }: { id: string }) {
  const { data, isPending, isError, error } = useQuery(userDetailOptions(id));

  if (isPending) return <Skeleton />;
  if (isError) return <ErrorMessage error={error} />;

  // 型別上 data 可能仍為 undefined，要再判斷一次
  return <div>{data?.name}</div>;
}
```

元件混雜資料載入狀態，邊界處理分散在每個 component。

## ✅ Good

```tsx
// 元件本體假設資料已存在
function UserProfile({ id }: { id: string }) {
  const { data } = useSuspenseQuery(userDetailOptions(id));
  return <div>{data.name}</div>; // data 型別非 undefined
}

// 外層處理 loading 與 error
<ErrorBoundary fallback={<ErrorMessage />}>
  <Suspense fallback={<Skeleton />}>
    <UserProfile id={id} />
  </Suspense>
</ErrorBoundary>;
```

搭配 Router 時，loader 已先呼叫 `ensureQueryData`，component 內 `useSuspenseQuery` 通常不會觸發 suspend，但仍保留型別保證與失敗時將錯誤拋向 ErrorBoundary 的能力。

## 例外

需要 `enabled` 條件式 fetch 或 `placeholderData` 時必須用 `useQuery`，因為 `useSuspenseQuery` 不支援這兩個選項。
