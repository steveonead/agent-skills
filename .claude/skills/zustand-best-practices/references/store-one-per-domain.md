---
rule: store-one-per-domain
category: Store 設計
tags: [store, architecture, naming]
---

# 一個 domain 一個 store

> 依 feature / domain 邊界拆分 store，避免把 UI 偏好、篩選條件、modal 狀態全部塞進同一個巨型 store。

## 原因

- 巨型 store 會讓不相關的 state 互相干擾，改一個欄位需要重新理解整顆 store
- Domain 邊界清楚才能局部測試、局部 reset、局部 persist
- 命名統一：`use` + Domain + `Store`，看名字就知道責任範圍

## ❌ Bad

```ts
import { create } from 'zustand';

// 一個 store 管 UI 偏好、列表篩選、modal、cart、auth ...
const useAppStore = create((set) => ({
  theme: 'light',
  sidebarOpen: true,
  userListSearch: '',
  userListRole: null,
  activeModal: null,
  cartItems: [],
  authToken: null,
  // ...
  actions: { /* 各種混在一起的 setter */ },
}));
```

任何細微修改都需在此檔案內反覆搜尋，PR diff 也容易與其他人產生衝突。

## ✅ Good

```ts
// stores/use-ui-store.ts
import { create } from 'zustand';

type UIStore = {
  theme: 'light' | 'dark';
  sidebarOpen: boolean;
  actions: {
    setTheme: (theme: UIStore['theme']) => void;
    toggleSidebar: () => void;
  };
};

export const useUIStore = create<UIStore>()((set) => ({
  theme: 'light',
  sidebarOpen: true,
  actions: {
    setTheme: (theme) => set({ theme }),
    toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  },
}));
```

```ts
// stores/use-user-filter-store.ts
import { create } from 'zustand';

type UserFilterStore = {
  search: string;
  role: string | null;
  actions: {
    setSearch: (search: string) => void;
    setRole: (role: string | null) => void;
  };
};

export const useUserFilterStore = create<UserFilterStore>()((set) => ({
  search: '',
  role: null,
  actions: {
    setSearch: (search) => set({ search }),
    setRole: (role) => set({ role }),
  },
}));
```

每個 store 各自一個檔案，責任邊界清楚，協作改動互不干擾。

## 例外

跨 domain 必須同步更新的 state（極少數情境），可以開一個 `useShared*Store` 或在元件層用 effect 串接，仍不應合併進其他 domain store。
