---
rule: token-theme-inline
category: Design Tokens
tags: [token, theme-inline, dark-mode, runtime]
---

# @theme inline 固化值，執行期主題切換會失效

> `@theme inline {}` 會在 build time 把 token 的值直接內聯進每個 utility，不保留 CSS 變數參照。若該 token 需要在執行期切換（dark mode、主題切換），用 `@theme inline` 會讓切換失效。需要執行期變動的 token 用一般 `@theme`。

## 原因

- 一般 `@theme` 讓 utility 透過 `var(--token)` 參照變數，改寫變數即可即時切換主題
- `@theme inline` 把值寫死進 utility，例如 `bg-surface` 直接變成 `background: #fff`，之後再改 `--surface` 變數也不會影響已生成的 utility
- 混用時容易誤判：明明改了變數畫面卻不變，排查成本高

## ❌ Bad

```css
/* surface 要隨 dark mode 切換，卻用 inline 固化 */
@theme inline {
  --color-surface: var(--bg);
}

:root {
  --bg: white;
}
.dark {
  --bg: black; /* bg-surface 已固化成 white，切不過去 */
}
```

## ✅ Good

```css
/* 需要執行期切換的 token 用一般 @theme，保留變數參照 */
@theme {
  --color-surface: var(--bg);
}

:root {
  --bg: white;
}
.dark {
  --bg: black; /* bg-surface 透過 var() 即時跟著切換 */
}
```

## 例外

token 值在執行期永遠不變（例如把第三方變數轉接成 Tailwind token，且不需主題切換）時，`@theme inline` 能少一層變數間接、輸出更精簡。
