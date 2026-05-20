---
rule: module-named-exports
category: module
tags: [module, export, default-export]
---

# 優先 named export

> 模組一律用 named export，禁止 `export default`。唯一白名單是「一個檔案只匯出一個元件」。

## 原因

- Named export 強制匯入端與匯出端名稱一致，避免同一模組在不同檔案被取不同名字
- IDE 的自動匯入、重新命名、引用搜尋對 named export 支援更完整
- Bundler 對 named export 的 tree-shaking 更精準

## ❌ Bad

```ts
// utils.ts
export default function formatDate(date: Date): string {
  return date.toLocaleDateString('zh-TW');
}

// consumer-a.ts
import formatDate from './utils';

// consumer-b.ts — 同一函式被取了不同名字
import dateFormatter from './utils';
```

每個 import 端都能自由命名，跨檔案搜尋 `formatDate` 會漏掉 `dateFormatter` 的使用。

## ✅ Good

```ts
// utils.ts
export function formatDate(date: Date): string {
  return date.toLocaleDateString('zh-TW');
}

export function formatCurrency(value: number): string {
  return `NT$ ${value.toLocaleString()}`;
}

// consumer.ts
import { formatDate, formatCurrency } from './utils';
```

匯入名稱與匯出名稱對齊，IDE 重構與全域搜尋都能正確運作。

## 例外

- 一個檔案只匯出一個元件（例如 `UserAvatar.tsx` 只 export 一個 `UserAvatar`），檔名即語意，且 `React.lazy()` 等動態載入要求 default export
