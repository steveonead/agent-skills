---
rule: performance-lazy-init-state
category: 效能
tags: [performance, useState, lazy-init]
---

# useState 昂貴初始值用 function form

> 昂貴的 `useState` 初始值（建立搜尋索引、解析 localStorage、運算轉換）必須用 function form `useState(() => value)`。每次 render 都會被求值的版本只能用於 primitive。

## 原因

- `useState(value)` 的 `value` 每次 render 都會被求值，即使只有初始 render 用得到
- Function form `useState(() => value)` React 只會在初始 render 呼叫一次
- 對 localStorage 讀取、JSON parse、建大型資料結構特別有效

## ❌ Bad

```tsx
// 每次 render 都跑 buildSearchIndex()
const [searchIndex, setSearchIndex] = useState(buildSearchIndex(items));

// 每次 render 都 JSON.parse
const [settings, setSettings] = useState(
  JSON.parse(localStorage.getItem('settings') ?? '{}'),
);
```

## ✅ Good

```tsx
// 只在初始 render 跑一次
const [searchIndex, setSearchIndex] = useState(() => buildSearchIndex(items));

// 只 parse 一次。實際專案應該用 zod 等 schema 驗證後再放入 state
type Settings = { theme: 'light' | 'dark'; locale: string };
const defaultSettings: Settings = { theme: 'light', locale: 'en' };

const [settings, setSettings] = useState<Settings>(() => {
  const stored = localStorage.getItem('settings');
  return stored ? JSON.parse(stored) : defaultSettings;
});
```

## 例外

- 簡單 primitive 初始值（`useState(0)`、`useState('')`、`useState(false)`）不需要 function form，求值便宜到忽略
- 從 props 直接帶入的初始值若已是 primitive，也不需要 wrap

## 同樣原則的姊妹規則

`useReducer(reducer, initialArg, init)` 的第三個參數 `init` 也是 lazy initializer，適合做同樣的優化。
