---
rule: perf-keep-selector-simple
category: 效能
tags: [performance, selector, custom-hook]
---

# Selector 保持單純，轉換放外部 hook

> Selector 內只做「從 state 拿值」，任何 `.map` / `.filter` / 物件組裝等轉換動作放到 custom hook 內處理。

## 原因

- Selector 每次 render 都會被執行，內部做 `.map` 或 new object 會回傳新 reference，被視為「值變了」而觸發 re-render
- 把 selector 拆成「取原始值」與「轉換」兩層，原始值是穩定的，轉換放在 hook 內配合 `useMemo` 或直接重算
- 配合 pmndrs 維護者建議：談的是「stable selector result」而非 stable selector function

## ❌ Bad

```ts
import { useStore } from './store';

export function usePetNames() {
  // 每次 render 都 .map 出新陣列，selector 結果 reference 永遠變
  return useStore((state) => state.pets.map((pet) => pet.name));
}
```

即使 `pets` 沒變，元件每次 render 都拿到新陣列，下游用到的元件會跟著 re-render。

## ✅ Good

```ts
import { useStore } from './store';

// Selector 只取原始值
function usePets() {
  return useStore((state) => state.pets);
}

// 轉換邏輯放在 hook 層，pets reference 穩定時結果也穩定
export function usePetNames() {
  const pets = usePets();
  return pets.map((pet) => pet.name);
}
```

`pets` 由 store 維護 reference 穩定，元件如果只在意名字列表，可進一步用 `useMemo` 包住 `.map` 結果：

```ts
import { useMemo } from 'react';

export function usePetNames() {
  const pets = usePets();
  return useMemo(() => pets.map((pet) => pet.name), [pets]);
}
```

## 例外

純粹回傳 primitive（`number`、`string`、`boolean`）的衍生計算可以直接寫在 selector 內，因為 primitive 本來就用值比較，不會有 reference 問題。
