---
rule: store-module-level-actions
category: Store 設計
tags: [store, actions, non-react]
---

# React 外用 module-level actions

> 需要在 React 元件外（router loader、utility function、event handler 內的非 React 程式碼）改 state 時，使用 module-level function 而非透過 hook。

## 原因

- Store 上的 `actions` 物件必須透過 hook 取得，hook 只能在 React 元件內呼叫
- Module-level function 是普通 function，可在任何地方執行
- 兩種寫法應共存：React 內走 `actions` 物件、React 外走 module-level function，分工清楚

## ❌ Bad

```ts
import { createFileRoute } from '@tanstack/react-router';
import { useStore } from './store';

export const Route = createFileRoute('/counter')({
  loader: () => {
    // loader 不是 React 元件，無法呼叫 hook 拿到 actions
    const { inc } = useStore((state) => state.actions); // 執行時拋錯
    inc();
  },
});
```

Loader、middleware、CLI script 皆不在 React 渲染樹內，在此呼叫 hook 會拋出錯誤。

## ✅ Good

```ts
import { create } from 'zustand';

type Store = {
  count: number;
};

export const useStore = create<Store>()(() => ({
  count: 0,
}));

// Module-level action：純 function，不依賴 hook
export function inc() {
  useStore.setState((state) => ({ count: state.count + 1 }));
}
```

```ts
import { createFileRoute } from '@tanstack/react-router';
import { inc } from './store';

export const Route = createFileRoute('/counter')({
  loader: () => {
    inc(); // 直接呼叫，不需要 hook
  },
});
```

React 內仍可保留 `actions` 物件給元件用；React 外需要操作 store 時，呼叫 module-level function 即可。
