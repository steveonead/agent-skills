---
rule: effect-primitive-deps
category: Effect 與副作用
tags: [effect, dependencies, performance]
---

# Effect 依賴用 primitive 值

> `useEffect` 的依賴陣列必須放 primitive 值（string、number、boolean）或衍生 boolean，禁止整包 object / array 直接放進去。`useMemo` / `useCallback` 原則相同，但在 React Compiler 環境下本來就應該避免手寫（見 `component-compiler-memo`），這條規則主要適用 `useEffect`。

## 原因

- 依賴整個 object 時，任何欄位變動都會觸發 effect，常導致無關 fetch / 重跑
- 連續變動的 number（如 `width`）會在每個 pixel 變化時都觸發 effect
- 拆出 primitive 或衍生 boolean，effect 只在真正關心的條件變動時跑

## ❌ Bad

```tsx
// user 任何欄位變了都會重跑
useEffect(() => {
  trackEvent('view', user.id);
}, [user]);

// width=767, 766, 765... 每個 pixel 都跑
useEffect(() => {
  if (width < 768) enableMobileMode();
}, [width]);

// filter 物件每次 render 都是新 reference
useEffect(() => {
  void fetchUsers(filter);
}, [filter]);
```

## ✅ Good

```tsx
// 只在 user.id 真的變了才重跑
useEffect(() => {
  trackEvent('view', user.id);
}, [user.id]);

// 只在 boolean 翻轉時跑
const isMobile = width < 768;
useEffect(() => {
  if (isMobile) enableMobileMode();
}, [isMobile]);

// 把 filter 拆成 primitive 欄位
useEffect(() => {
  void fetchUsers({ search: filter.search, status: filter.status });
}, [filter.search, filter.status]);
```

## 例外

- 依賴的 object 來自 server data 且 reference 已經穩定（例如 TanStack Query cache 回傳的同一個物件），可以直接放
- 依賴本身就是 array length 等少數 primitive 衍生時，列 length 比列整個 array 安全
