---
rule: token-css-vars
category: Design Tokens
tags: [token, css-variables, theme-function]
---

# 用 var(--color-blue-500) 取代 theme('colors.blue.500')

> 在自訂 CSS 中取用 design token，改用 v4 自動暴露的 CSS 變數 `var(--color-blue-500)`，不再用 `theme('colors.blue.500')` 函式。

## 原因

- v4 把 `@theme` 內所有 token 自動暴露成 `:root` 上的 CSS 變數，直接 `var()` 取用最直接
- `theme()` 函式雖仍可用，但官方建議改用 CSS 變數，後者支援執行期覆蓋、能被 dev tools 檢視
- CSS 變數可在執行期被 media query、`.dark` class 或 JS 改寫，`theme()` 在 build time 就固定了

## ❌ Bad

```css
.alert {
  /* theme() 在 build time 固化，無法執行期覆蓋 */
  background-color: theme('colors.blue.500');
  margin-block: theme('spacing.4');
}
```

## ✅ Good

```css
.alert {
  /* 直接用 v4 暴露的 CSS 變數 */
  background-color: var(--color-blue-500);
  margin-block: var(--spacing-4);
}
```

## 例外

需要在 build time 對 token 值做數值運算（例如傳進不接受 `var()` 的 CSS 函式參數）時，仍可用 `theme()` 取出固定值。
