---
rule: directive-screen
category: CSS 指令
tags: [directive, media-query, breakpoint, removed]
---

# @screen 已移除，改用 @media screen(sm)

> v4 移除了 `@screen sm {}` 指令。在 CSS 中要套用斷點的 media query，改用 `@media screen(sm) {}` 函式語法，或直接用 theme 變數寫 `@media (width >= theme(--breakpoint-sm))`。

## 原因

- `@screen` 在 v4 已不存在，沿用會直接編譯錯誤
- `screen()` 函式會解析成對應的 media query，語意與 v3 `@screen` 一致
- 多數情況根本不需要寫 media query，直接在 markup 用 `sm:` 變體即可

## ❌ Bad

```css
.card {
  padding: 1rem;
}

/* v4 已移除 @screen，編譯失敗 */
@screen sm {
  .card {
    padding: 2rem;
  }
}
```

## ✅ Good

```css
.card {
  padding: 1rem;
}

/* 用 screen() 函式對應斷點 */
@media screen(sm) {
  .card {
    padding: 2rem;
  }
}
```

更好的做法是回到 markup 用變體，不寫自訂 media query：

```html
<div class="p-4 sm:p-8">...</div>
```

## 例外

無法改 markup 的第三方內容、或需在 CSS 內封裝複雜 responsive 邏輯時，才在 CSS 寫 `@media screen(sm)`。
