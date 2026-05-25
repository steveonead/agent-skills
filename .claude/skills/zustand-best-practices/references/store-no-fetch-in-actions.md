---
rule: store-no-fetch-in-actions
category: Store 設計
tags: [store, actions, server-state, blocker]
---

# 🚨 不在 actions 內做 data fetching

> Zustand action 只負責 `set()` 改 client state，禁止 `fetch`、`axios` 或任何 server data 請求；data fetching 一律交給 TanStack Query。

## 原因

- 在 action 內自行實作 fetch，等同於重新打造一個缺少 retry、cache、dedup 的 TanStack Query
- Server state 與 client state 分流：Zustand 管 UI / 偏好 / 暫時 state，TanStack Query 管遠端資料
- 把 server 資料複製進 Zustand 會造成兩份資料源，極易過期、極難同步

## ❌ Bad

```ts
import { create } from 'zustand';

const useStore = create((set) => ({
  users: [],
  loading: false,
  actions: {
    // 自行實作 fetch，缺少 retry、cache 與 stale 控制機制
    fetchUsers: async () => {
      set({ loading: true });
      const users = await fetch('/api/users').then((r) => r.json());
      set({ users, loading: false });
    },
  },
}));
```

一旦多個元件同時呼叫 `fetchUsers`，會送出重複請求；server 資料變動後 Zustand 內的版本也不會自動失效。

## ✅ Good

```ts
import { create } from 'zustand';

type UIState = {
  sidebarOpen: boolean;
  actions: {
    toggleSidebar: () => void;
  };
};

// Zustand：只管 UI / client state
export const useUIStore = create<UIState>()((set) => ({
  sidebarOpen: true,
  actions: {
    toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  },
}));
```

```ts
import { queryOptions } from '@tanstack/react-query';

// TanStack Query：管 server state
export function userListOptions() {
  return queryOptions({
    queryKey: ['users'],
    queryFn: () => fetch('/api/users').then((r) => r.json()),
  });
}
```

各司其職：UI 開關交由 Zustand 管理，遠端資料交由 Query 處理，兩者邊界清楚、互不干涉。
