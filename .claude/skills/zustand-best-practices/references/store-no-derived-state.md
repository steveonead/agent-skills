---
rule: store-no-derived-state
category: Store 設計
tags: [store, derived-state, selector]
---

# Derived state 用 selector 計算，不寫進 store

> 任何可由現有 state 推導出來的值（如「是否有套用篩選」、「總數」、「篩選後的清單」）用 selector 即時計算，不要存成 store 欄位。

## 原因

- Derived state 存成欄位後需要在每個 setter 同步更新，容易遺漏導致資料不一致
- Zustand selector 本來就會在依賴變動時重算，效能上不會比手動同步差
- Store 只保留「真正的 source of truth」，閱讀時更容易判斷誰是來源、誰是衍生

## ❌ Bad

```ts
import { create } from 'zustand';

type FilterStore = {
  search: string;
  role: string | null;
  hasActiveFilter: boolean; // 衍生欄位
  actions: {
    setSearch: (search: string) => void;
    setRole: (role: string | null) => void;
  };
};

export const useFilterStore = create<FilterStore>()((set) => ({
  search: '',
  role: null,
  hasActiveFilter: false,
  actions: {
    // 每個 setter 都需同步更新 hasActiveFilter，遺漏任一處即會產生 bug
    setSearch: (search) =>
      set((state) => ({ search, hasActiveFilter: search !== '' || state.role !== null })),
    setRole: (role) =>
      set((state) => ({ role, hasActiveFilter: state.search !== '' || role !== null })),
  },
}));
```

未來新增第三個篩選條件（如 `status`）時，前兩個 setter 內的 `hasActiveFilter` 計算就會漏掉那個條件。

## ✅ Good

```ts
import { create } from 'zustand';

type FilterStore = {
  search: string;
  role: string | null;
  actions: {
    setSearch: (search: string) => void;
    setRole: (role: string | null) => void;
  };
};

export const useFilterStore = create<FilterStore>()((set) => ({
  search: '',
  role: null,
  actions: {
    setSearch: (search) => set({ search }),
    setRole: (role) => set({ role }),
  },
}));

// Derived value 走 selector hook
export function useHasActiveFilter() {
  return useFilterStore((state) => state.search !== '' || state.role !== null);
}
```

新增條件只要修改 selector 一處，store 內不再混雜衍生欄位。
