---
rule: store-initial-state-object
category: Store 設計
tags: [store, initial-state, reset]
---

# initialState 抽成獨立物件

> Store 的初始 state 抽成獨立常數，建立 store 與 `reset` action 都引用同一份，避免新增欄位時兩邊不同步。

## 原因

- `reset()` 需要把 state 還原到初始值，如果在 action 內硬寫一份初始值，每次新增欄位都要同步兩處
- 獨立物件讓「初始 state 長什麼樣」一目瞭然，方便測試 setup
- 行為一致：建立時與 reset 後的 state shape 完全相同

## ❌ Bad

```ts
import { create } from 'zustand';

type Filter = {
  search: string;
  role: string | null;
  status: string | null;
  actions: {
    reset: () => void;
  };
};

export const useFilterStore = create<Filter>()((set) => ({
  search: '',
  role: null,
  status: null,
  actions: {
    // reset 內又寫一次初始值，新增欄位時很容易漏改
    reset: () => set({ search: '', role: null, status: null }),
  },
}));
```

日後新增 `sort` 欄位時，create 處已補上，reset 卻容易遺漏，導致 reset 後 sort 仍保留舊值。

## ✅ Good

```ts
import { create } from 'zustand';

type FilterState = {
  search: string;
  role: string | null;
  status: string | null;
};

type FilterStore = FilterState & {
  actions: {
    reset: () => void;
  };
};

const initialState: FilterState = {
  search: '',
  role: null,
  status: null,
};

export const useFilterStore = create<FilterStore>()((set) => ({
  ...initialState,
  actions: {
    reset: () => set(initialState),
  },
}));
```

新增欄位只要改 `initialState` 一處，create 與 reset 同步更新。
