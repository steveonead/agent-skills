---
rule: router-type-safe-navigation
category: Router 路由與導航
tags: [router, navigation, Link, useNavigate, type-safety]
---

# 用 `<Link>` / `useNavigate({ from })` 維持 type-safe navigation

> 跨頁導航統一用 TanStack Router 的 `<Link to>` 或 `useNavigate({ from })`，禁用 `window.location.href` 賦值、`history.pushState` 直接操作、或 plain `<a href>` 內部跳轉。`useNavigate` 必須帶 `from` 才能讓 relative path 與 search params 推導型別。

## 原因

- TanStack Router 的型別安全依賴其自身的導航 API，若改用原生跳轉將失去靜態檢查保護
- `<Link to="/users/$userId" params={{ userId }}>` 由 router 於編譯期檢查路徑、params、search 是否合法
- `useNavigate({ from })` 的 `from` 告知 TypeScript 當前所在的 route，後續 relative path 與 search 變更才能取得型別推導
- `window.location.href` 會觸發整頁重新載入，繞過 router 的 cache、loader、preload，破壞 SPA 的整體運作機制

## ❌ Bad

```tsx
// 觸發整頁重新載入，cache 與 state 將全數清除
<a href={`/users/${userId}`}>View User</a>;

button.onclick = () => {
  window.location.href = "/dashboard";
};

// 未指定 from，relative path 無法正確推導型別
const navigate = useNavigate();
navigate({ to: "../settings" }); // 型別錯誤
```

## ✅ Good

```tsx
import { Link, useNavigate } from "@tanstack/react-router";

// Link 元件 —— 編譯期型別檢查
<Link
  to="/users/$userId"
  params={{ userId }}
  search={{ tab: "profile" }}
>
  View User
</Link>;

// useNavigate 指定 from
function UserActions() {
  const navigate = useNavigate({ from: "/users/$userId" });

  const handleEdit = () => {
    navigate({
      to: "./edit", // relative 解析為 /users/$userId/edit
    });
  };

  const handleHome = () => navigate({ to: "/" });
}
```

外部連結（離開站台）仍用 `<a target="_blank" rel="noopener noreferrer">`，這條規則只規範站內導航。

## 例外

OAuth callback、付款導回等需要真正離開 SPA 再進來的場景，用 `window.location.href` 是正確的。重點是「站內導航不要繞過 router」。
