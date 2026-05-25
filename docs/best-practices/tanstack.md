---
title: TanStack 最佳實踐
---

# TanStack 最佳實踐

<!-- 此檔案由 scripts/generate-best-practice.mjs 自動產生，請勿直接編輯 -->
<!-- 來源：.claude/skills/tanstack-best-practices/ -->

<details open>
<summary>🚨 BLOCKER 規則一覽</summary>

- [2.3 loaderDeps 讓 Search Params 成為 Cache Key](#_2-3-🚨-loaderdeps-讓-search-params-成為-cache-key)

</details>

## 1. Query — 資料管理

### 1.1 用 queryOptions 統一管理 Query 定義

> Query key factory 管 key 結構，`queryOptions()` 管完整 query 定義，必須在 component、loader、prefetch 間共享同一份定義。禁止在多處重複定義 query key。

**原因**

- Query key 散落各處會在 invalidation 時踩坑（key 不一致導致 invalidate 失敗）
- `queryOptions()` 把 key + fn + options 打包成可重用物件，確保一致性
- component、loader、prefetch 共用同一個定義，修改只需改一處

**❌ Bad**

```ts
// query key 散落各處，容易不一致
// component
const { data } = useQuery({
  queryKey: ['users', 'detail', id],
  queryFn: () => fetchUser(id),
});

// loader — key 結構不同，invalidation 會踩坑
context.queryClient.ensureQueryData({
  queryKey: ['user', id], // 少了 'detail' 層級
  queryFn: () => fetchUser(id),
});
```

**✅ Good**

```ts
// query key factory — 管 key 結構
export const userKeys = {
  all: ['users'] as const,
  lists: () => [...userKeys.all, 'list'] as const,
  list: (params: ListParams) => [...userKeys.lists(), params] as const,
  details: () => [...userKeys.all, 'detail'] as const,
  detail: (id: string) => [...userKeys.details(), id] as const,
};

// queryOptions() — 管完整 query 定義
import { queryOptions } from '@tanstack/react-query';

export function userDetailOptions(id: string) {
  return queryOptions({
    queryKey: userKeys.detail(id),
    queryFn: () => fetchUser(id),
    staleTime: 5 * 60 * 1000,
  });
}

// component
const { data } = useQuery(userDetailOptions(id));

// loader
context.queryClient.ensureQueryData(userDetailOptions(id));

// hover prefetch
queryClient.prefetchQuery(userDetailOptions(id));
```

### 1.2 設定全域 staleTime

> 禁止使用 TanStack Query 預設的 `staleTime: 0`，全域預設必須至少設 30 秒。

**原因**

- TanStack Query 預設 `staleTime: 0`，每次元件 mount 都會 refetch
- 大多數應用的資料不需要即時更新，30 秒甚至 5 分鐘的 stale 完全可接受
- 不設 staleTime 會導致不必要的網路請求與 UI 閃爍

**❌ Bad**

```ts
// 使用預設 staleTime: 0 — 每次 mount 都 refetch
const queryClient = new QueryClient();
```

**✅ Good**

```ts
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // 全域預設：30 秒內不 refetch
      staleTime: 30 * 1000,
    },
  },
});

// Dashboard 類型可以更長
export function dashboardStatsOptions() {
  return queryOptions({
    queryKey: ['dashboard', 'stats'],
    queryFn: fetchDashboardStats,
    staleTime: 5 * 60 * 1000, // 5 分鐘
  });
}
```

### 1.3 用 invalidateQueries 取代 setQueryData

> Mutation 成功後用 `invalidateQueries` 讓 query 自己 refetch，不手動維護 cache。允許場景：需要 optimistic update 時搭配 `onMutate` + `onError` rollback 使用 `setQueryData`。

**原因**

- 手動 `setQueryData` 需要維護 cache 正確性、處理 list/detail 不一致、pagination cache 更新
- `invalidateQueries` 讓 TanStack Query 自動 refetch，保證資料一致性
- 九成情況下省一次 request 的收益遠不及手動維護 cache 的複雜度

#### 白名單

以下情況允許使用 `setQueryData`：

- **Optimistic update**：需要在 mutation 回傳前立即更新 UI 時，搭配 `onMutate` + `onError` rollback 使用

**❌ Bad**

```ts
const mutation = useMutation({
  mutationFn: updateUser,
  onSuccess: updatedUser => {
    // 手動更新 cache — 需處理 list cache、detail cache、pagination 等
    queryClient.setQueryData(userKeys.detail(updatedUser.id), updatedUser);
    // 忘了更新 list cache → 列表頁顯示舊資料
  },
});
```

**✅ Good**

```ts
const mutation = useMutation({
  mutationFn: updateUser,
  onSuccess: () => {
    // 讓相關 query 自己 refetch
    queryClient.invalidateQueries({ queryKey: userKeys.all });
  },
});
```

### 1.4 使用 keepPreviousData 優化分頁體驗

> 分頁或 filter 切換時，使用 `placeholderData: keepPreviousData` 讓前一頁資料持續顯示，無縫切換到新資料。

**原因**

- 沒有 `keepPreviousData`，切換頁面時 UI 會閃成 skeleton 再載入完成
- 一行設定就能讓使用者體驗從「閃爍」變成「無縫切換」
- `isPlaceholderData` flag 可用來顯示過渡狀態（如半透明效果）

**❌ Bad**

```tsx
function UserList({ page }: { page: number }) {
  const { data, isPending } = useQuery(userListOptions(page));

  // 每次換頁都閃成 skeleton
  if (isPending) return <Skeleton />;

  return (
    <div>
      {data.users.map(user => (
        <UserRow key={user.id} user={user} />
      ))}
    </div>
  );
}
```

**✅ Good**

```tsx
import { useQuery, keepPreviousData } from '@tanstack/react-query';

function UserList({ page }: { page: number }) {
  const { data, isPlaceholderData } = useQuery({
    ...userListOptions(page),
    placeholderData: keepPreviousData,
  });

  return (
    <div style={{ opacity: isPlaceholderData ? 0.5 : 1 }}>
      {data?.users.map(user => (
        <UserRow key={user.id} user={user} />
      ))}
    </div>
  );
}
```

### 1.5 用 select 轉換 Query 資料減少 Re-render

> 使用 `useQuery` 的 `select` option 在 subscription 層級轉換或篩選資料，元件只在 selected 值改變時 re-render。TanStack Query 透過 structural sharing（`replaceEqualDeep`）自動保留 reference 穩定性。

**原因**

- 不用 `select`，元件訂閱整個 query response，任何欄位變更都觸發 re-render
- `select` 只回傳需要的子集或衍生值，減少不必要的 re-render
- structural sharing 確保 `select` 回傳值相同時保留 reference，不會產生新物件觸發 re-render

**❌ Bad**

```ts
// 訂閱整個 user 物件，任何欄位變更都 re-render
function UserName({ userId }: { userId: string }) {
  const { data: user } = useQuery(userDetailOptions(userId));
  return <span>{user?.name}</span>;
}
```

**✅ Good**

```ts
import { useQuery, queryOptions } from '@tanstack/react-query';

export function userDetailOptions(id: string) {
  return queryOptions({
    queryKey: userKeys.detail(id),
    queryFn: () => fetchUser(id),
  });
}

// 只訂閱 name，user 其他欄位變了不會 re-render
function UserName({ userId }: { userId: string }) {
  const { data: userName } = useQuery({
    ...userDetailOptions(userId),
    select: (user) => user.name,
  });
  return <span>{userName}</span>;
}

// 從 array 提取 id list
function UserIdList() {
  const { data: userIds } = useQuery({
    ...userListOptions(),
    select: (users) => users.map((user) => user.id),
  });
  return <IdList ids={userIds} />;
}
```

### 1.6 Hover 時 Prefetch 提升導航體驗

> 在連結或按鈕的 `onMouseEnter` / `onFocus` 事件中呼叫 `queryClient.prefetchQuery()`，讓使用者點擊時資料已在 cache 中，導航瞬間完成。必須搭配 `queryOptions()` factory 確保 prefetch 與 component 使用同一份 query 定義。

**原因**

- 不做 prefetch，使用者點擊後才開始載入，需要等待 loader 完成才能看到頁面
- `prefetchQuery` 在 hover 時就把資料載入 cache，後續 `ensureQueryData` 直接命中 cache
- 搭配 `queryOptions()` factory 確保 prefetch 與 component 用的是同一份 query 定義，避免 cache miss

**❌ Bad**

```tsx
// 沒有 prefetch — 每次導航都要等 loader 從 server 載完
function UserLink({ userId }: { userId: string }) {
  return (
    <Link to="/users/$userId" params={{ userId }}>
      View User
    </Link>
  );
}
```

**✅ Good**

```tsx
import { useQueryClient } from '@tanstack/react-query';
import { Link } from '@tanstack/react-router';

function UserLink({ userId }: { userId: string }) {
  const queryClient = useQueryClient();

  function handlePrefetch() {
    queryClient.prefetchQuery(userDetailOptions(userId));
  }

  return (
    <Link
      to="/users/$userId"
      params={{ userId }}
      onMouseEnter={handlePrefetch}
      onFocus={handlePrefetch}
    >
      View User
    </Link>
  );
}
```

## 2. Router — 路由載入

### 2.1 Loader 搭配 ensureQueryData 消除 Waterfall

> 在 route 的 `loader` 裡用 `ensureQueryData` 提前載入資料，禁止等元件 mount 後才發請求。

**原因**

- 等元件 mount 後才用 `useQuery` 發請求，會產生 request waterfall
- `loader` 在導航時就開始載入，元件 mount 時資料已在 cache 中
- 搭配 `queryOptions()` factory 確保 loader 與 component 使用同一份 query 定義

**❌ Bad**

```tsx
// 沒有 loader — 元件 mount 後才開始載入
export const Route = createFileRoute('/users/$userId')({
  component: UserPage,
});

function UserPage() {
  const { userId } = Route.useParams();
  // mount 後才發請求，產生 waterfall
  const { data, isPending } = useQuery(userDetailOptions(userId));
  if (isPending) return <Skeleton />;
  return <UserProfile user={data} />;
}
```

**✅ Good**

```ts
import { createFileRoute } from '@tanstack/react-router';
import { useSuspenseQuery } from '@tanstack/react-query';

export const Route = createFileRoute('/users/$userId')({
  loader: async ({ context: { queryClient }, params: { userId } }) => {
    // 導航時就開始載入，不等元件 mount
    await queryClient.ensureQueryData(userDetailOptions(userId));
  },
  component: UserPage,
});

function UserPage() {
  const { userId } = Route.useParams();
  // 資料已在 cache，不會 suspend
  const { data } = useSuspenseQuery(userDetailOptions(userId));
  return <UserProfile user={data} />;
}
```

### 2.2 beforeLoad 做認證守衛

> 禁止在元件內做認證檢查與跳轉，必須在 `beforeLoad` 用 `throw redirect()` 阻止受保護頁面的任何 render。

**原因**

- 在元件裡 `if (!user) navigate('/login')` 會先閃一下目標頁面再跳轉
- `beforeLoad` 在元件 render 前執行，使用者完全看不到受保護內容
- `throw redirect()` 能阻止後續的 loader 和 component render

**❌ Bad**

```tsx
function Dashboard() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated) {
      // 元件已經 render 了才跳轉 — 會閃一下
      navigate({ to: '/login' });
    }
  }, [isAuthenticated, navigate]);

  return <DashboardContent />;
}
```

**✅ Good**

```ts
import { createFileRoute, redirect } from '@tanstack/react-router';

export const Route = createFileRoute('/dashboard')({
  beforeLoad: ({ context }) => {
    if (!context.auth.isAuthenticated) {
      // 使用者連 dashboard 的 render 都不會看到
      throw redirect({ to: '/login' });
    }
  },
  loader: async ({ context: { queryClient } }) => {
    await queryClient.ensureQueryData(dashboardOptions());
  },
  component: Dashboard,
});
```

### 2.3 🚨 loaderDeps 讓 Search Params 成為 Cache Key

> 當 loader 依賴 search params 時，必須透過 `loaderDeps` 宣告依賴，否則 Router 不會因 search params 變更而重新執行 loader。

**原因**

- TanStack Router 預設不會因為 search params 變更而重新執行 loader
- `loaderDeps` 告訴 Router 哪些 search params 變化需要觸發 loader 重新執行
- 搭配 URL state 管理，確保分頁、filter 等狀態與資料同步

**❌ Bad**

```ts
export const Route = createFileRoute('/posts')({
  // 沒有 loaderDeps — search params 改了 loader 不會重跑
  loader: async ({ context: { queryClient } }) => {
    await queryClient.ensureQueryData(postListOptions(1)); // 永遠只載第一頁
  },
  component: PostList,
});
```

**✅ Good**

```ts
export const Route = createFileRoute('/posts')({
  loaderDeps: ({ search }) => ({ page: search.page }),
  loader: async ({ context: { queryClient }, deps }) => {
    // deps.page 改變時 loader 會重新執行
    await queryClient.ensureQueryData(postListOptions(deps.page));
  },
  component: PostList,
});
```

### 2.4 Deferred Data Loading 分離關鍵與非關鍵資料

> 關鍵資料用 `ensureQueryData`（await），非關鍵資料用 `prefetchQuery`（不 await）+ `<Suspense>`。

**原因**

- 所有資料都 await 會延長導航時間，使用者等待感增加
- 非關鍵資料（留言、推薦）不需要阻塞導航
- `prefetchQuery` 不 await，背景載入；元件端用 `useSuspenseQuery` + `<Suspense>` 消費

#### 分類說明

| 情境                   | loader 做法                      | 需要手動 `<Suspense>`？                                           |
| ---------------------- | -------------------------------- | ----------------------------------------------------------------- |
| 關鍵資料               | `await ensureQueryData(...)`     | 不需要——資料已進 cache，Router 的 `pendingComponent` 處理 loading |
| 非關鍵（deferred）資料 | `prefetchQuery(...)`（不 await） | **需要**——資料可能尚未 resolve，必須手動包 `<Suspense>`           |

**❌ Bad**

```tsx
export const Route = createFileRoute('/posts/$postId')({
  loader: async ({ context: { queryClient }, params: { postId } }) => {
    // 全部 await — 使用者要等所有資料載完才能看到頁面
    await queryClient.ensureQueryData(postQueryOptions(postId));
    await queryClient.ensureQueryData(commentsQueryOptions(postId));
  },
  component: PostPage,
});
```

**✅ Good**

```tsx
export const Route = createFileRoute('/posts/$postId')({
  loader: async ({ context: { queryClient }, params: { postId } }) => {
    // 非關鍵 → prefetchQuery（不 await，背景載入）
    queryClient.prefetchQuery(commentsQueryOptions(postId));
    // 關鍵 → ensureQueryData（await，阻塞導航直到完成）
    await queryClient.ensureQueryData(postQueryOptions(postId));
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
    </>
  );
}

function Comments({ postId }: { postId: string }) {
  const { data } = useSuspenseQuery(commentsQueryOptions(postId));
  return <CommentList data={data} />;
}
```

### 2.5 pendingMs / pendingMinMs 防閃爍

> 設定 `defaultPendingMs` 與 `defaultPendingMinMs`，控制 loading UI 的顯示時機與最短持續時間，防止快速載入時的閃爍。

**原因**

- 沒設 `pendingMs`，每次導航都立刻顯示 loading indicator，即使資料 50ms 就回來
- 沒設 `pendingMinMs`，loading UI 可能只出現 100ms 就消失，造成閃爍
- 全域設定一次，所有 route 受益

**✅ Good**

```ts
import { createRouter } from '@tanstack/react-router';

const router = createRouter({
  // 超過 500ms 才顯示 pending UI
  defaultPendingMs: 500,
  // 顯示後至少維持 800ms，避免閃爍
  defaultPendingMinMs: 800,
  defaultPendingComponent: () => <GlobalSpinner />,
});
```

### 2.6 用 zodValidator + Zod Schema 驗證 Search Params

> 所有有 search params 的 route 必須透過 `validateSearch: zodValidator(schema)` 搭配 Zod schema 做型別驗證。禁止直接存取未經驗證的 search params。必須使用 `@tanstack/zod-adapter` 的 `fallback()` 處理預設值，禁止使用 Zod 原生的 `.catch()`。

**原因**

- 不用 `validateSearch`，search params 是 `unknown`，需要手動 `as` 斷言，失去型別安全
- Zod schema 提供 runtime validation + 自動 TypeScript 型別推導，一處定義兩端受益
- `fallback()` 讓無效的 URL 參數自動退回預設值，使用者貼錯 URL 不會白畫面
- `zodValidator` 是 TanStack Router 官方推薦的 Zod 整合方式，禁止直接傳 Zod schema 給 `validateSearch`

**❌ Bad**

```ts
// 沒有 validateSearch — search params 是 unknown
export const Route = createFileRoute('/products')({
  loader: async ({ context: { queryClient } }) => {
    // 沒有型別 — 需要手動 as 斷言
    await queryClient.ensureQueryData(productListOptions({ page: 1 }));
  },
  component: ProductListPage,
});

function ProductListPage() {
  // search 是 unknown，要自己 parse 且沒有型別安全
  const search = Route.useSearch();
}
```

**✅ Good**

```ts
import { createFileRoute } from '@tanstack/react-router';
import { zodValidator, fallback } from '@tanstack/zod-adapter';
import { z } from 'zod';

const productSearchSchema = z.object({
  page: fallback(z.number(), 1).default(1),
  sort: fallback(z.enum(['newest', 'price', 'rating']), 'newest').default(
    'newest',
  ),
  category: fallback(z.string(), '').default(''),
});

export type ProductSearch = z.infer<typeof productSearchSchema>;

export const Route = createFileRoute('/products')({
  validateSearch: zodValidator(productSearchSchema),
  loaderDeps: ({ search }) => ({ page: search.page, sort: search.sort }),
  loader: async ({ context: { queryClient }, deps }) => {
    await queryClient.ensureQueryData(productListOptions(deps));
  },
  component: ProductListPage,
});
```

### 2.7 用 select 精準訂閱 Search Params 減少 Re-render

> 使用 `Route.useSearch({ select })` 精準訂閱特定 search params，元件只在 selected 值改變時 re-render。回傳物件時必須啟用 `structuralSharing: true` 避免 reference 不穩定。

**原因**

- 直接使用 `Route.useSearch()` 訂閱所有 search params，任何一個參數變更都觸發 re-render
- `select` 只訂閱需要的參數子集，其他參數變更不影響元件
- 回傳物件時 `select` 每次產生新 reference，必須啟用 `structuralSharing` 讓 Router 用 deep equal 保留穩定 reference

**❌ Bad**

```tsx
// 訂閱所有 search params — page 變了 sort、category 相關元件也 re-render
function Pagination() {
  const search = Route.useSearch();
  return <PageIndicator current={search.page} />;
}
```

**✅ Good**

```ts
// 只訂閱 page，其他 search params 變了不會 re-render
function Pagination() {
  const page = Route.useSearch({ select: (search) => search.page });
  return <PageIndicator current={page} />;
}

// 回傳物件時啟用 structuralSharing 避免 reference 不穩定
function ActiveFilters() {
  const filters = Route.useSearch({
    select: (search) => ({
      sort: search.sort,
      category: search.category,
    }),
    structuralSharing: true,
  });
  return <FilterBadges filters={filters} />;
}
```
