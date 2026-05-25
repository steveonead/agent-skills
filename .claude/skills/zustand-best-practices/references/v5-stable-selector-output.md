---
rule: v5-stable-selector-output
category: v5 升級
tags: [v5, migration, selector, infinite-loop, blocker]
---

# 🚨 Selector 必須回傳 stable reference

> Zustand v5 對齊 React 預設行為：selector 每次回傳新建立的物件或陣列會被視為「值變了」，連鎖觸發 re-render，極易踩到 infinite loop。確保 selector 結果穩定，或在不得已時包 `useShallow`。

## 原因

- v5 移除 store 層級 equality，selector 結果預設用 `Object.is` 比較
- Inline 建立的 `{}` 或 `[]` 每次 render 都是新 reference，被認為「改變」
- 連續更新會觸發 React 的更新次數上限保護，拋出 `Maximum update depth exceeded` 錯誤

## ❌ Bad

```tsx
import { useStore } from './store';

function Profile() {
  // 每次 render 都建立新物件，selector 結果永遠不等於上一次
  // v5 會直接視為「值變了」，配上 useEffect 連鎖就會 infinite loop
  const profile = useStore((state) => ({
    name: state.name,
    email: state.email,
  }));

  return <div>{profile.name} / {profile.email}</div>;
}
```

升級到 v5 後常見錯誤訊息：

```
Warning: Maximum update depth exceeded.
```

## ✅ Good — 取 primitive 維持穩定

```tsx
import { useStore } from './store';

function Profile() {
  const name = useStore((state) => state.name);
  const email = useStore((state) => state.email);

  return <div>{name} / {email}</div>;
}
```

各欄位獨立訂閱 primitive，預設以 `Object.is` 比較，reference 自然維持穩定。

## ✅ Good — 不得已要回物件時包 `useShallow`

```tsx
import { useShallow } from 'zustand/react/shallow';
import { useStore } from './store';

function Profile() {
  const profile = useStore(
    useShallow((state) => ({ name: state.name, email: state.email })),
  );

  return <div>{profile.name} / {profile.email}</div>;
}
```

`useShallow` 會 memoize selector 結果：當回傳物件 shallow-equal 時沿用上次的 reference，避免不必要的 re-render。
