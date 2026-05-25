---
rule: middleware-devtools-persist-order
category: Middleware
tags: [middleware, devtools, persist, order, blocker]
---

# 🚨 Middleware 順序：devtools 外、persist 內

> 同時使用 `devtools` 與 `persist` 時，`devtools` 必須包在最外層、`persist` 包在內層，禁止反向嵌套。

## 原因

- `devtools` 包外層才能觀察到所有 state 變更，包含 `persist` 的 rehydration 過程
- 反過來嵌套會讓 DevTools 看不到從 storage 還原進來的 state，debug 時極為困難
- 這是 Zustand 官方文件採用的順序，與社群慣例一致

## ❌ Bad

```ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

const useStore = create<State>()(
  // persist 在外、devtools 在內 — DevTools 看不到 rehydration
  persist(
    devtools((set) => ({
      /* ... */
    })),
    { name: 'my-store' },
  ),
);
```

Storage 還原時的 state 變化不會被 DevTools 紀錄，重新整理頁面後 DevTools 的 history 就斷了。

## ✅ Good

```ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

const useStore = create<State>()(
  devtools(
    persist(
      (set) => ({
        /* ... */
      }),
      { name: 'my-store' },
    ),
  ),
);
```

DevTools 監聽 `persist` 之後的 state，rehydration 也被當成一次 state 更新紀錄下來，整個 debug 流程連貫。
