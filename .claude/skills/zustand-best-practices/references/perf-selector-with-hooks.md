---
rule: perf-selector-with-hooks
category: 效能
tags: [performance, selector, custom-hook, blocker]
---

# 🚨 透過 selector + custom hooks 取值

> 禁止直接 `useStore()` 訂閱整個 store；任何取值都要透過 selector 精準訂閱，並封裝成 custom hook 供元件使用。

## 原因

- 直接 `useStore()` 會訂閱整顆 store，任一欄位變動都會觸發 re-render
- Selector 只訂閱被選到的 slice，re-render 範圍縮到最小
- Custom hook 把 store 結構封裝在 hook 內，元件不直接耦合 store 欄位名稱，未來改 schema 容易

## ❌ Bad

```tsx
import { useStore } from './store';

function Counter() {
  // 訂閱整顆 store，name 或其他欄位變動也會 re-render
  const store = useStore();
  return <span>{store.count}</span>;
}
```

只想顯示 `count`，卻會因為 `name`、`theme` 等不相關欄位變動跟著 re-render。

## ✅ Good

```ts
// store.ts
import { create } from 'zustand';

type States = {
  count: number;
  name: string;
};

type Actions = {
  actions: {
    inc: () => void;
    setName: (name: string) => void;
  };
};

export const useStore = create<States & Actions>()((set) => ({
  count: 0,
  name: '',
  actions: {
    inc: () => set((state) => ({ count: state.count + 1 })),
    setName: (name) => set({ name }),
  },
}));

// Custom selector hooks
export function useCount() {
  return useStore((state) => state.count);
}

export function useName() {
  return useStore((state) => state.name);
}

export function useStoreActions() {
  return useStore((state) => state.actions);
}
```

```tsx
import { useCount } from './store';

function Counter() {
  const count = useCount();
  return <span>{count}</span>;
}
```

`Counter` 只在 `count` 真的變動時 re-render，其他 state 異動完全不影響。
