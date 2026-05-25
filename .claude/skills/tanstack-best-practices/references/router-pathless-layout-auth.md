---
rule: router-pathless-layout-auth
category: Router 路由與導航
tags: [router, file-based-routing, auth, layout, pathless-route]
---

# 認證守衛集中在 `_authenticated` pathless layout

> 多個 route 都需要登入時，建立 pathless layout route（檔名以 `_` 開頭），把 `beforeLoad` 認證守衛放在這個 layout，所有子 route 自動受保護。禁止在每個 protected route 重複 copy-paste 認證邏輯。

## 原因

- 將 auth 守衛分散於每個 route 容易遺漏：新增 route 時若遺漏守衛，將造成資安漏洞
- Pathless layout（`_authenticated.tsx`）不會在 URL 中產生 segment，僅用於包裝子路由
- File-based routing 下，所有放置於 `_authenticated/` 目錄底下的 route 會自動繼承該 layout 的 `beforeLoad`

## ❌ Bad

```
src/routes/
  dashboard.tsx     ← 各自實作 beforeLoad
  settings.tsx      ← 各自實作 beforeLoad
  billing.tsx       ← 未加守衛，存在資安風險
```

```ts
// dashboard.tsx
export const Route = createFileRoute("/dashboard")({
  beforeLoad: ({ context }) => {
    if (!context.auth.isAuthenticated) throw redirect({ to: "/login" });
  },
  // ...
});

// settings.tsx
export const Route = createFileRoute("/settings")({
  beforeLoad: ({ context }) => {  // 重複
    if (!context.auth.isAuthenticated) throw redirect({ to: "/login" });
  },
  // ...
});

// billing.tsx —— 遺漏 beforeLoad
export const Route = createFileRoute("/billing")({
  loader: ({ context }) => context.queryClient.ensureQueryData(billingOptions()),
  component: BillingPage, // 未登入使用者仍可存取此頁面
});
```

## ✅ Good

```
src/routes/
  _authenticated.tsx        ← pathless layout，集中 beforeLoad
  _authenticated/
    dashboard.tsx
    settings.tsx
    billing.tsx
  login.tsx                 ← 不在 _authenticated 底下，公開
```

```tsx
// _authenticated.tsx
import { createFileRoute, Outlet, redirect } from "@tanstack/react-router";

export const Route = createFileRoute("/_authenticated")({
  beforeLoad: ({ context, location }) => {
    if (!context.auth.isAuthenticated) {
      throw redirect({
        to: "/login",
        search: { redirect: location.href },
      });
    }
    return { user: context.auth.user };
  },
  component: () => <Outlet />,
});
```

```ts
// _authenticated/billing.tsx —— 無需重複實作 auth guard
export const Route = createFileRoute("/_authenticated/billing")({
  loader: ({ context }) =>
    context.queryClient.ensureQueryData(billingOptions(context.user.id)),
  component: BillingPage,
});
```

`beforeLoad` 回傳的 `{ user }` 會合併進 context，子 route 的 loader 可直接以 `context.user` 取得，且型別會自動推導。

## 例外

不同層級的權限（admin vs. user）可進一步嵌套：`_authenticated/_admin/...`，於 admin layout 再加一層權限檢查。
