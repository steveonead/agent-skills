---
rule: config-no-js
category: 設定方式
tags: [config, theme, css-first]
---

# 自訂 theme 改用 CSS @theme，不用 JS config 的 theme.extend

> v4 採 CSS-first 設定。自訂 design token（顏色、間距、字級、斷點等）寫在 CSS 的 `@theme {}` 區塊，不再用 `tailwind.config.js` 的 `theme.extend`。

## 原因

- v4 預設不讀 `tailwind.config.js`，舊的 `theme.extend` 寫了也不會生效，必須額外用 `@config` 指令載入才會被讀到
- `@theme` 內的 token 會自動產生對應 utility 並暴露成 CSS 變數，JS config 做不到後者
- 設定與樣式同在 CSS，少一層 JS 與 CSS 之間的對應心智負擔

## ❌ Bad

```js
// tailwind.config.js — v4 預設根本不會讀這個檔
export default {
  theme: {
    extend: {
      colors: {
        brand: { 500: '#3b82f6' },
      },
      spacing: {
        18: '4.5rem',
      },
    },
  },
};
```

## ✅ Good

```css
/* app.css */
@import 'tailwindcss';

@theme {
  --color-brand-500: #3b82f6;
  --spacing-18: 4.5rem;
}
```

`--color-brand-500` 會生成 `bg-brand-500`、`text-brand-500` 等 utility，同時可用 `var(--color-brand-500)` 在任意 CSS 中取用。

## 例外

需要動態運算 token、或暫時與既有 v3 config 並存的 migration 過渡期，可用 `@config "../tailwind.config.js";` 顯式載入舊 config。這是過渡手段，migration 完成後應移除。
