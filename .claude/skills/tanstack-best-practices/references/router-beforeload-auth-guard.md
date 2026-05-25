---
rule: router-beforeload-auth-guard
category: Router 路由與導航
tags: [router, auth, beforeLoad, redirect]
---

# `beforeLoad` + `throw redirect()` 做認證守衛

> 認證、權限、subscription 等 access control 必須在 `beforeLoad` 用 `throw redirect()` 阻擋，禁止在 component 內用 `useEffect` + `navigate()` 跳轉。

## 原因

- 在 component 內以 `useEffect` 執行跳轉時，受保護內容已先 render 一次，使用者會短暫看見該畫面
- `beforeLoad` 於 component render 之前執行，`throw redirect()` 直接中斷流程，後續 loader 與 component 皆不會執行
- `beforeLoad` 由上而下依序執行，可於父層完成認證，子層自動受其保護

## ❌ Bad

```tsx
function Dashboard() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated) {
      navigate({ to: "/login" }); // 已 render dashboard 後才執行跳轉
    }
  }, [isAuthenticated, navigate]);

  if (!isAuthenticated) return null; // 畫面仍會短暫出現空白
  return <DashboardContent />;
}
```

## ✅ Good

```ts
import { createFileRoute, redirect } from "@tanstack/react-router";

export const Route = createFileRoute("/dashboard")({
  beforeLoad: ({ context, location }) => {
    if (!context.auth.isAuthenticated) {
      throw redirect({
        to: "/login",
        search: { redirect: location.href },
      });
    }
  },
  loader: ({ context }) =>
    context.queryClient.ensureQueryData(dashboardOptions()),
  component: Dashboard,
});

function Dashboard() {
  // 執行至此已確保使用者登入，無需重複判斷
  const { data } = useSuspenseQuery(dashboardOptions());
  return <DashboardContent data={data} />;
}
```

需要在登入後跳回原頁面：

```tsx
// login route
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { zodValidator } from "@tanstack/zod-adapter";
import { z } from "zod";

export const Route = createFileRoute("/login")({
  validateSearch: zodValidator(z.object({ redirect: z.string().optional() })),
  component: LoginPage,
});

function LoginPage() {
  const { redirect } = Route.useSearch();
  const navigate = useNavigate();
  return (
    <LoginForm
      onSuccess={() => navigate({ to: redirect ?? "/" })}
    />
  );
}
```

## 例外

非阻塞的權限提示（例如「升級到 Pro」橫幅）不需 redirect，在 component 內判斷顯示即可。
