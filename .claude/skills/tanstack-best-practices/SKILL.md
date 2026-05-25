---
name: tanstack-best-practices
description: TanStack Query v5 與 TanStack Router 最佳實踐規則集，供撰寫、審查或重構 TanStack 相關程式碼時參考。明確要求 Vite + React SPA、file-based routing 環境，搭配 React Compiler annotation mode。適用於新功能開發、PR self-review、TanStack Query v4 → v5 migration。不適用於 SSR、TanStack Start、Next.js App Router、純 Server Component 情境。
---

# TanStack Best Practices

這份規則集針對 TanStack Query v5 + TanStack Router 在 Vite SPA 環境的搭配使用。Query 規則特別強調 v5 與 v4 的差異（如 `useSuspenseQuery` 一級公民、移除 `onSuccess`/`onError`/`onSettled`、`queryOptions()` API、`placeholderData: keepPreviousData` 等），Router 規則聚焦 file-based routing、loader / beforeLoad / search params 驗證、與 Query 的整合。

## 適用時機

- 撰寫新的 Query / Router 程式碼
- 審查既有程式碼是否使用 v5 API 與型別安全模式
- TanStack Query v4 → v5 migration
- 對 AI 產出的 Query / Router 程式碼做對齊

## 規則分類

| 分類 | 前綴 | 條數 |
|------|------|------|
| Query 資料管理 | `query-` | 9 |
| Router 路由與導航 | `router-` | 9 |
| Query + Router 整合 | `integration-` | 1 |

## 規則速查

### Query 資料管理

- `query-options-factory` — 用 `queryOptions()` 統一管理 query 定義，跨 component / loader / prefetch 共享同一份
- `query-set-global-staletime` — 全域 `staleTime` 至少 30 秒，禁用預設值 0
- `query-suspense-first` — 預設 `useSuspenseQuery` + Suspense + ErrorBoundary，不在 component 內分支 `isPending` / `isError`
- `query-no-effect-callbacks` — `useQuery` 在 v5 移除 `onSuccess` / `onError` / `onSettled`，禁止使用
- `query-placeholderdata-keep-previous` — 分頁或篩選用 `placeholderData: keepPreviousData`（v5 名稱）
- `query-no-derived-state` — 不要把 query data 同步進 `useState` 或外部 store，直接訂閱
- `query-invalidate-over-setdata` — Mutation 後預設 `invalidateQueries`，僅 optimistic update 才用 `setQueryData`
- `query-mutation-declarative-invalidation` — 用 `MutationCache` 全域 `onSuccess` + `meta.invalidates` 集中宣告 mutation 影響的 keys
- `query-mutation-optimistic-flow` — Optimistic update 必須走 `onMutate` → `cancelQueries` → `onError` rollback → `onSettled` invalidate 完整流程

### Router 路由與導航

- `router-create-router-config` — `createRouter()` 必設 context.queryClient、`defaultPreload: 'intent'`、`defaultPreloadStaleTime: 0`
- `router-loader-ensure-data` — Route loader 用 `ensureQueryData` 消除 waterfall
- `router-beforeload-auth-guard` — `beforeLoad` + `throw redirect()` 守衛，不在 component 內 useEffect 跳轉
- `router-pathless-layout-auth` — 認證守衛集中在 `_authenticated.tsx` pathless layout
- `router-loaderdeps-search` 🚨 — loader 依賴 search params 必須宣告 `loaderDeps`
- `router-zod-validator-search` — `validateSearch: zodValidator(schema)` + `fallback()` 驗證 search params
- `router-deferred-loading` — 關鍵資料 `await ensureQueryData`、非關鍵不 await `prefetchQuery` + `<Suspense>`
- `router-state-components` — Route 必須提供 `errorComponent` / `notFoundComponent` / `pendingComponent`
- `router-type-safe-navigation` — 用 `<Link>` / `useNavigate({ from })`，禁用 `window.location.href`

### Query + Router 整合

- `integration-shared-queryoptions` — `<Link>` hover prefetch、loader `ensureQueryData`、component `useSuspenseQuery` 必須使用同一份 `queryOptions()` 工廠

## 使用方式

讀取個別規則檔案以取得詳細說明與範例：

```
references/[類別前綴]-[規則名稱].md
```

每個規則檔案包含：
- 為何此規則重要
- 不建議的寫法（含說明）
- 建議的寫法（含說明）
- 補充說明與例外

## 環境前提

這份規則集假設：
- **Vite SPA**：純客戶端渲染，不涉及 SSR / HydrationBoundary / TanStack Start
- **React Compiler annotation mode**：需手動加 `"use memo"` 才會自動 memo，但本規則集不要求 manual `useMemo` / `useCallback`，僅在需要 stable reference 的場景明示
- **File-based routing**：所有範例使用 `createFileRoute('/path')`

## 參考來源

- [TanStack Query v5 Docs](https://tanstack.com/query/v5/docs)
- [TanStack Router Docs](https://tanstack.com/router/latest/docs)
- [TkDodo's Blog — Automatic Query Invalidation after Mutations](https://tkdodo.eu/blog/automatic-query-invalidation-after-mutations)
- [Announcing TanStack Query v5](https://tanstack.com/blog/announcing-tanstack-query-v5)
