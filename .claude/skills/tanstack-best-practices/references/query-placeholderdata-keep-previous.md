---
rule: query-placeholderdata-keep-previous
category: Query 資料管理
tags: [query, pagination, placeholderData, keepPreviousData]
---

# 分頁或篩選用 `placeholderData: keepPreviousData`

> 切換頁碼、排序、filter 時用 `placeholderData: keepPreviousData`（v5 寫法），讓前一頁資料持續顯示直到新資料到位。禁用 v4 的 `keepPreviousData: true` option。

## 原因

- v5 將 `keepPreviousData: true` option 改為 `placeholderData: keepPreviousData` 函式，後者支援自訂 placeholder 計算，彈性較高
- 未設定 placeholderData 時，切換頁面會閃回 skeleton 畫面，影響使用者體驗
- `isPlaceholderData` flag 可標示「正在切換」，可用於顯示過渡動畫或半透明效果

## ❌ Bad

```tsx
// v4 寫法 —— v5 不支援
const { data } = useQuery({
  ...postListOptions(page),
  keepPreviousData: true,
});

// 未設定 placeholderData —— 每次換頁畫面會回到 skeleton
function PostList({ page }: { page: number }) {
  const { data, isPending } = useQuery(postListOptions(page));
  if (isPending) return <Skeleton />;
  return <List items={data.posts} />;
}
```

## ✅ Good

```tsx
import { keepPreviousData, useQuery } from "@tanstack/react-query";

function PostList({ page }: { page: number }) {
  const { data, isPlaceholderData } = useQuery({
    ...postListOptions(page),
    placeholderData: keepPreviousData,
  });

  return (
    <div style={{ opacity: isPlaceholderData ? 0.5 : 1 }}>
      <List items={data?.posts ?? []} />
    </div>
  );
}
```

注意此規則的 `useQuery` 不能換成 `useSuspenseQuery`：後者不支援 `placeholderData`。需要 suspense + 分頁的場景，改用 `useQuery` 並在外層自行包 fallback，或用 `useSuspenseInfiniteQuery` 改為 infinite scroll。

## 例外

無分頁、無 filter 切換的單一資源 query 不需要設定。
