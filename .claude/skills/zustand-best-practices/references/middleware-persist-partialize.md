---
rule: middleware-persist-partialize
category: Middleware
tags: [middleware, persist, partialize]
---

# 用 `partialize` 只持久化必要的 state

> 使用 `persist` middleware 時必須提供 `partialize`，明確列出要進入 storage 的欄位；暫時性 UI state（modal 開關、loading、選取項）不得進 storage。

## 原因

- `persist` 預設會把整個 store 寫入 storage，包含本應只活在記憶體裡的暫時 state
- 暫時 state 被持久化，會導致下次進入頁面時殘留上次未關閉的 modal、loading 狀態無法清除等非預期行為
- `partialize` 是明確 whitelist，看一眼就知道哪些是「跨 session 偏好」、哪些是「暫時 UI」

## ❌ Bad

```ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

const useUIStore = create<States & Actions>()(
  devtools(
    persist(
      (set) => ({
        theme: 'light',
        locale: 'zh-TW',
        sidebarOpen: true,
        modalStack: [],
        actions: {
          /* ... */
        },
      }),
      { name: 'ui-store' }, // 沒有 partialize，sidebarOpen 與 modalStack 也被寫進 storage
    ),
  ),
);
```

使用者上次離開時未關閉的 modal，下次進入頁面時會再次顯示，行為類似 bug。

## ✅ Good

```ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

type States = {
  theme: 'light' | 'dark';
  locale: string;
  sidebarOpen: boolean;
  modalStack: string[];
};

type Actions = {
  actions: {
    setTheme: (theme: States['theme']) => void;
    toggleSidebar: () => void;
  };
};

const useUIStore = create<States & Actions>()(
  devtools(
    persist(
      (set) => ({
        theme: 'light',
        locale: 'zh-TW',
        sidebarOpen: true,
        modalStack: [],
        actions: {
          setTheme: (theme) => set({ theme }),
          toggleSidebar: () =>
            set((state) => ({ sidebarOpen: !state.sidebarOpen })),
        },
      }),
      {
        name: 'ui-store',
        // 只保留跨 session 的使用者偏好
        partialize: (state) => ({
          theme: state.theme,
          locale: state.locale,
        }),
      },
    ),
  ),
);
```

只有 `theme` 與 `locale` 寫進 storage，暫時 UI state 重新開啟時都回到預設值。
