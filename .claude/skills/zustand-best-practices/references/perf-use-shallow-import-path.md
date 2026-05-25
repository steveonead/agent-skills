---
rule: perf-use-shallow-import-path
category: 效能
tags: [performance, useShallow, import, blocker, v5]
---

# 🚨 `useShallow` 從 `zustand/react/shallow` import

> 在 React 元件內使用 `useShallow` 時，必須 import 自 `zustand/react/shallow`，不要從 `zustand/shallow` 或其他路徑取得。

## 原因

- `zustand/react/shallow` 暴露的是 React hook 版本，會走 `useMemo` 確保 selector 結果穩定
- `zustand/shallow` 暴露的是純比較函式（給 vanilla store 或自訂 equality 使用），在 React 元件內直接傳給 selector 並不會 memo selector function 本身
- Import 錯路徑通常還是能跑，但 selector 每次 render 都是新的 reference，等於失去 `useShallow` 應有的優化效果

## ❌ Bad

```tsx
import { useStore } from './store';
import { shallow } from 'zustand/shallow'; // 只是比較函式

function Profile() {
  // shallow 是純比較函式，在 v5 的 create 已無法傳第二參數，
  // 即使能跑也不會 memo 這個 inline selector
  const { name, email } = useStore(
    (state) => ({ name: state.name, email: state.email }),
    shallow,
  );
  return <div>{name} / {email}</div>;
}
```

在 v5 環境內，這段甚至連型別都不會通過（`create` 不再接受 equalityFn）。

## ✅ Good

```tsx
import { useShallow } from 'zustand/react/shallow';
import { useStore } from './store';

function Profile() {
  const { name, email } = useStore(
    useShallow((state) => ({ name: state.name, email: state.email })),
  );
  return <div>{name} / {email}</div>;
}
```

`useShallow` 會 memo selector function，並在執行結果 shallow-equal 時保持 reference，達成「同樣的物件不重新觸發 re-render」的效果。
