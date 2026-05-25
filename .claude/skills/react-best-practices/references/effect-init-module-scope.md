---
rule: effect-init-module-scope
category: Effect 與副作用
tags: [effect, initialization, strict-mode]
---

# App 初始化放 module scope

> App-level 的一次性初始化（讀 storage、驗證 token、註冊全域 listener）必須用 module-level guard 確保只跑一次，禁止單純依賴 `useEffect(fn, [])`。

## 原因

- React Strict Mode 在 dev 會故意把 effect 跑兩次，揭露未清理乾淨的副作用
- 路由切換或父層 remount 會讓元件重新 mount，`useEffect(fn, [])` 又會再跑一次
- Module-level guard 只在 module 第一次被 import 時執行，是真正的「整個 app 一次」

## ❌ Bad

```tsx
// dev 跑兩次，re-mount 又跑一次
function App() {
  useEffect(() => {
    loadFromStorage();
    checkAuthToken();
  }, []);

  return <RouterProvider router={router} />;
}
```

## ✅ Good

```tsx
let didInit = false;

function App() {
  useEffect(() => {
    if (didInit) return;
    didInit = true;
    loadFromStorage();
    checkAuthToken();
  }, []);

  return <RouterProvider router={router} />;
}
```

或更乾脆，直接在 module top-level 執行：

```tsx
// 真正只在 module 載入時跑一次
loadFromStorage();
checkAuthToken();

function App() {
  return <RouterProvider router={router} />;
}
```

## 判斷準則

- 純粹「app 啟動一次」的邏輯（讀 localStorage、初始化 SDK）→ module top-level 或 module guard
- 需要存取 props / state 才能跑的初始化 → 仍然用 `useEffect`，但要寫對 cleanup
