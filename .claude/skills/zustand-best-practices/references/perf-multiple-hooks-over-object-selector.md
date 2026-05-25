---
rule: perf-multiple-hooks-over-object-selector
category: 效能
tags: [performance, selector, useShallow]
---

# 取多值優先多次呼叫 hook

> 需要從 store 取多個欄位時，預設多次呼叫 selector hook；只有當元件真的需要「一個物件」時，才用 `useShallow` 包成單一物件。

## 原因

- Zustand v5 維護者直接推薦的寫法：多次呼叫 hook，每個都是 primitive selector，最直觀也最容易讓型別正確
- 多次呼叫不會有效能損失，每個 selector 各自獨立訂閱
- `useShallow` 是工具，不是預設手段；只在「要 destructure 單一物件、且該物件是新建立」時才需要

## ❌ Bad

```tsx
import { useShallow } from 'zustand/react/shallow';
import { useStore } from './store';

function Profile() {
  // 只是要拿 name 跟 email，硬包成物件再 useShallow，多此一舉
  const { name, email } = useStore(
    useShallow((state) => ({ name: state.name, email: state.email })),
  );

  return <div>{name} / {email}</div>;
}
```

每新增一個欄位，selector 內就要補上一行 key-value，型別宣告也較為冗長。

## ✅ Good

```tsx
import { useStore } from './store';

function Profile() {
  const name = useStore((state) => state.name);
  const email = useStore((state) => state.email);

  return <div>{name} / {email}</div>;
}
```

兩次 hook 呼叫各自訂閱對應 slice，re-render 邏輯與單一 selector 完全等價，型別也最直觀。

## 例外

下列情境才適合用 `useShallow` 包成物件：
1. 元件邏輯內部需要把這些值當「一組物件」傳遞（例如 `useEffect` 的 dependency 想以物件對應）
2. Selector 是動態組合（例如根據 id 從 list 篩出一個物件）

```ts
import { useShallow } from 'zustand/react/shallow';

export function usePet(id: string) {
  return useStore(
    useShallow((state) => state.pets.find((pet) => pet.id === id)),
  );
}
```
