---
rule: component-no-store-inside-component
category: 元件慣例
tags: [component, singleton, create]
---

# Store 必為 module-level singleton

> `create()` 只能在 module top-level 呼叫，禁止寫在 React 元件、hook 或 callback 內部。

## 原因

- 在元件內呼叫 `create()`，每次 render 都會建立一份新的 store，state 永遠回到初始值
- Store 是「跨元件共享的單一資料來源」，必須在 module 載入時就建立好
- Module top-level 的 store 自然是 singleton，多處 import 拿到的是同一個實例

## ❌ Bad

```tsx
import { create } from 'zustand';

function Counter() {
  // 每次 render 都建立新的 store，count 持續回到 0，inc 看似無效
  const useStore = create<{ count: number; inc: () => void }>()((set) => ({
    count: 0,
    inc: () => set((state) => ({ count: state.count + 1 })),
  }));

  const { count, inc } = useStore();

  return <button onClick={inc}>{count}</button>;
}
```

點擊後 `inc` 雖然有執行，但下一次 render 會拿到全新的 store，畫面停留在 `0`。

## ✅ Good

```ts
// stores/use-counter-store.ts
import { create } from 'zustand';

type CounterStore = {
  count: number;
  actions: {
    inc: () => void;
  };
};

export const useCounterStore = create<CounterStore>()((set) => ({
  count: 0,
  actions: {
    inc: () => set((state) => ({ count: state.count + 1 })),
  },
}));
```

```tsx
// components/counter.tsx
import { useCounterStore } from '@/stores/use-counter-store';

export function Counter() {
  const count = useCounterStore((state) => state.count);
  const { inc } = useCounterStore((state) => state.actions);

  return <button onClick={inc}>{count}</button>;
}
```

Store 是 module 載入時建立的單一實例，所有元件共用同一份 state，行為穩定可預期。
