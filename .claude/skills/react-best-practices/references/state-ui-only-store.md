---
rule: state-ui-only-store
category: 狀態管理
tags: [state, store, zustand, scope]
---

# Client state store 只放純 UI 狀態

> Global client state store（Zustand / Jotai / Redux）只能放純 UI 狀態：sidebar 開合、modal 顯示、theme、command palette 等。禁止存 server data、可從 URL 推導的狀態、form state。

## 原因

- Server data 應該交給 server-state cache（TanStack Query），它已內建 dedup、refetch、cache invalidation
- 可分享的 state（page、sort、filter）應該放 URL search params
- Store 越小越好，只放真正屬於 client 的 UI 狀態，降低除錯與重構成本

## ❌ Bad

```ts
// store 混了 server data、URL state、form state
const useStore = create<Store>()(set => ({
  // ✓ UI state
  sidebarOpen: true,
  // ✗ server data — 該由 TanStack Query 管
  users: [],
  // ✗ URL state — 該放 search params
  currentPage: 1,
  sortBy: 'name',
  // ✗ form state — 該在元件 local 或 react-hook-form
  emailInput: '',
}));
```

## ✅ Good

```ts
type UIState = {
  sidebarOpen: boolean;
  theme: 'light' | 'dark';
  commandPaletteOpen: boolean;
  actions: {
    toggleSidebar: () => void;
    setTheme: (theme: 'light' | 'dark') => void;
    openCommandPalette: () => void;
    closeCommandPalette: () => void;
  };
};

const useUIStore = create<UIState>()(set => ({
  sidebarOpen: true,
  theme: 'light',
  commandPaletteOpen: false,
  actions: {
    toggleSidebar: () => set(state => ({ sidebarOpen: !state.sidebarOpen })),
    setTheme: theme => set({ theme }),
    openCommandPalette: () => set({ commandPaletteOpen: true }),
    closeCommandPalette: () => set({ commandPaletteOpen: false }),
  },
}));
```

## 狀態分類速查

| 類型 | 範例 | 應該放哪 |
| --- | --- | --- |
| Server data | API response、列表資料、單筆內容 | TanStack Query |
| URL state | page、sort、filter、tab | URL search params（TanStack Router） |
| Form state | 表單欄位值、validation 訊息 | 元件 local state 或 react-hook-form |
| Pure UI state | sidebar、modal、theme、command palette | Client state store |
| Component local | counter、toggle、focus state | `useState` |
