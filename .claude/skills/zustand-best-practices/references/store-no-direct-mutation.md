---
rule: store-no-direct-mutation
category: Store 設計
tags: [store, immutability, setState]
---

# `set()` 內不可直接 mutate state

> Updater function 內禁止直接修改傳入的 `state` 參數，必須回傳新物件；Zustand 預設用 shallow merge，靠 reference 變化偵測更新。

## 原因

- Zustand 的訂閱機制比較 reference，直接 mutate 不會改 reference，selector 拿不到變化
- 看起來像有寫入卻不會 re-render 的 bug 極難排查
- 若需要可變語法（deeply nested update），用 `immer` middleware，而不是直接 mutate

## ❌ Bad

```ts
import { create } from 'zustand';

type TodoStore = {
  todos: { id: string; done: boolean }[];
  actions: {
    toggle: (id: string) => void;
  };
};

export const useTodoStore = create<TodoStore>()((set) => ({
  todos: [],
  actions: {
    toggle: (id) =>
      set((state) => {
        const target = state.todos.find((todo) => todo.id === id);
        if (target) {
          target.done = !target.done; // 直接 mutate 陣列內的物件
        }
        return state; // 同一個 reference，訂閱者收不到變化
      }),
  },
}));
```

在部分情境下 mutation 看似生效（同次 render 內可讀到新值），但元件不會 re-render，UI 持續停留在舊狀態。

## ✅ Good

```ts
import { create } from 'zustand';

type TodoStore = {
  todos: { id: string; done: boolean }[];
  actions: {
    toggle: (id: string) => void;
  };
};

export const useTodoStore = create<TodoStore>()((set) => ({
  todos: [],
  actions: {
    toggle: (id) =>
      set((state) => ({
        todos: state.todos.map((todo) =>
          todo.id === id ? { ...todo, done: !todo.done } : todo,
        ),
      })),
  },
}));
```

回傳新的陣列與新的 todo 物件，reference 改變，訂閱該 slice 的元件正常 re-render。

## 例外

需要操作深層巢狀 state（3 層以上）時，導入 `immer` middleware，在 immer 提供的 draft 上 mutate，由 immer 負責產生新 reference。
