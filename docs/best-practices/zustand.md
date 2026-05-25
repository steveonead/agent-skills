---
title: Zustand 最佳實踐
---

# Zustand 最佳實踐

<!-- 此檔案由 scripts/generate-best-practice.mjs 自動產生，請勿直接編輯 -->
<!-- 來源：.claude/skills/zustand-best-practices/ -->

<details open>
<summary>🚨 BLOCKER 規則一覽</summary>

- [1.3 不在 Actions 裡放 fetch 邏輯](#_1-3-🚨-不在-actions-裡放-fetch-邏輯)
- [2.1 用 Selector + Hooks 取值](#_2-1-🚨-用-selector-hooks-取值)
- [3.1 Middleware 順序：devtools 外、persist 內](#_3-1-🚨-middleware-順序-devtools-外、persist-內)

</details>

## 1. Store 設計

### 1.1 Action 定義在 Store 的 actions 物件

> 禁止在元件中直接操作 `setState`，所有 action 必須集中在 store 的 `actions` 物件中。

**原因**

- 邏輯集中管理，可測試、可追蹤，不會散落在各元件中
- 元件只呼叫語意化的 action（如 `actions.addItem(item)`），不直接操作 state
- `actions` 物件的 reference 穩定，不會觸發 re-render

**❌ Bad**

```tsx
function Counter() {
  const setState = useStore.setState;

  // 元件直接操作 state — 邏輯散落各處
  function handleInc() {
    setState(prev => ({ count: prev.count + 1 }));
  }

  return <button onClick={handleInc}>+</button>;
}
```

**✅ Good**

```ts
import { create } from 'zustand';

type States = {
  count: number;
};

type Actions = {
  actions: {
    inc: () => void;
    dec: () => void;
  };
};

const useStore = create<States & Actions>()(set => ({
  count: 1,
  actions: {
    inc: () => set(state => ({ count: state.count + 1 })),
    dec: () => set(state => ({ count: state.count - 1 })),
  },
}));
```

### 1.2 Module-level Actions 適用 React 外部

> 在 React 元件外部（loader、utility function）需要呼叫 action 時，用 module-level actions。

**原因**

- Store 內的 `actions` 物件需要透過 hook 存取，只能在 React 元件內使用
- Module-level actions 是普通函式，不需要 hook 即可呼叫
- 適用於 router loader、middleware、utility function 等場景

**✅ Good**

```ts
export const useStore = create(() => ({ count: 0 }));

// Module-level action — 不需要在 React 元件內呼叫
export function inc() {
  useStore.setState(state => ({ count: state.count + 1 }));
}

// 在 router loader 中使用
export const Route = createFileRoute('/counter')({
  loader: () => {
    inc(); // 直接呼叫，不需要 hook
  },
});
```

**關鍵規則**

- 團隊應統一選擇一種 pattern，或明確區分使用場景
- **React 內**：用 store 的 `actions` 物件
- **React 外**：用 module-level actions

### 1.3 🚨 不在 Actions 裡放 fetch 邏輯

> Zustand actions 禁止包含 `fetch` 或任何 data fetching 邏輯，只做 `set()` 改變 client state。所有 data fetching 必須由 TanStack Query 處理。

**原因**

- 在 Zustand action 裡寫 `fetch()` 等於在重新發明一個更差的 TanStack Query
- TanStack Query 提供 retry、background sync、dedup、cache invalidation，Zustand 都沒有
- 職責分離：Zustand 管 UI state，TanStack Query 管 server state

**❌ Bad**

```ts
// 在 Zustand 裡做 fetch — 沒有 retry、cache、dedup
const useStore = create(set => ({
  users: [],
  loading: false,
  actions: {
    fetchUsers: async () => {
      set({ loading: true });
      const users = await fetch('/api/users').then(r => r.json());
      set({ users, loading: false });
    },
  },
}));
```

**✅ Good**

```ts
// Zustand — 只管 UI state
const useUIStore = create<UIState>()(set => ({
  sidebarOpen: true,
  actions: {
    toggleSidebar: () => set(s => ({ sidebarOpen: !s.sidebarOpen })),
  },
}));

// TanStack Query — 管 data fetching
export function userListOptions() {
  return queryOptions({
    queryKey: userKeys.lists(),
    queryFn: fetchUsers,
  });
}
```

## 2. 效能

### 2.1 🚨 用 Selector + Hooks 取值

> 禁止直接呼叫 `useStore()` 訂閱整個 store，必須透過 selector 精準取值，並封裝為 custom hooks。

**原因**

- 直接使用 `useStore()` 會訂閱整個 store，任何 state 變更都觸發 re-render
- Selector 只訂閱需要的 slice，減少不必要的 re-render
- 封裝成 custom hooks 讓元件不直接依賴 store 結構

**❌ Bad**

```ts
function Counter() {
  // 訂閱整個 store — name 變了也會 re-render
  const store = useStore();
  return <span>{store.count}</span>;
}
```

**✅ Good**

```ts
import { useShallow } from 'zustand/react/shallow';

type States = {
  count: number;
  name: string;
};

type Actions = {
  actions: {
    inc: () => void;
    dec: () => void;
  };
};

const useStore = create<States & Actions>()(set => ({
  count: 1,
  name: '',
  actions: {
    inc: () => set(state => ({ count: state.count + 1 })),
    dec: () => set(state => ({ count: state.count - 1 })),
  },
}));

// 單一值 selector
export function useCount() {
  return useStore(state => state.count);
}

// 衍生值 selector
export function useDoubledCount() {
  return useStore(state => state.count * 2);
}

// actions 永遠穩定，不會觸發 re-render
export function useStoreActions() {
  return useStore(state => state.actions);
}

// 多值用 useShallow 避免 reference 不穩定
export function useParams() {
  return useStore(
    useShallow(state => ({ count: state.count, name: state.name })),
  );
}
```

## 3. Middleware

### 3.1 🚨 Middleware 順序：devtools 外、persist 內

> `devtools` 必須包在最外層，`persist` 包在內層。禁止反向嵌套。

**原因**

- 反過來會導致 devtools 無法正確追蹤 persist 的 hydration 過程
- `devtools` 在外層才能觀察到所有 state 變更（包含 persist rehydration）
- 這是 Zustand 官方推薦的嵌套順序

**❌ Bad**

```ts
const useStore = create<State>()(
  persist(
    devtools(set => ({
      /* ... */
    })),
    { name: 'my-store' },
  ),
);
```

**✅ Good**

```ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

const useStore = create<State>()(
  devtools(
    persist(
      set => ({
        /* ... */
      }),
      { name: 'my-store' },
    ),
  ),
);
```

### 3.2 用 partialize 只持久化必要的 State

> 使用 `persist` middleware 時，必須透過 `partialize` 明確指定要持久化的欄位。禁止讓 `persist` 預設存取整個 store，暫時性 UI state（如 modal、sidebar、loading）不得持久化。

**原因**

- `persist` 預設會將整個 store 存入 storage，包含暫時性 UI state（modal 開關、sidebar 狀態）
- 暫時性 state 被持久化會導致重新開啟頁面時出現非預期的 UI 狀態
- `partialize` 明確 whitelist 需要持久化的欄位，語意清晰、不會意外存入不該存的資料

**❌ Bad**

```ts
// persist 預設存所有 state — sidebarOpen、modalStack 也被存了
const useUIStore = create<States & Actions>()(
  devtools(
    persist(
      set => ({
        theme: 'light',
        locale: 'zh-TW',
        sidebarOpen: true,
        modalStack: [],
        actions: {
          setTheme: theme => set({ theme }),
          toggleSidebar: () =>
            set(state => ({ sidebarOpen: !state.sidebarOpen })),
        },
      }),
      { name: 'ui-store' }, // 沒有 partialize — 全部都被存了
    ),
  ),
);
```

**✅ Good**

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
      set => ({
        theme: 'light',
        locale: 'zh-TW',
        sidebarOpen: true,
        modalStack: [],
        actions: {
          setTheme: theme => set({ theme }),
          toggleSidebar: () =>
            set(state => ({ sidebarOpen: !state.sidebarOpen })),
        },
      }),
      {
        name: 'ui-store',
        // 只持久化使用者偏好，不存暫時性 UI state
        partialize: state => ({ theme: state.theme, locale: state.locale }),
      },
    ),
  ),
);
```
