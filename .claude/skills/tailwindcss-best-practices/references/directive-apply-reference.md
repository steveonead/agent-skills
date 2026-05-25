---
rule: directive-apply-reference
category: CSS 指令
tags: [directive, apply, reference, css-module, scoped]
---

# scoped CSS 中用 @apply 需先加 @reference，不用 @import

> 在 CSS Module、Vue `<style scoped>`、或任何與主 CSS 分開編譯的檔案中使用 `@apply`，要在檔案頂部加 `@reference "../app.css";` 讓編譯器知道 theme 定義。不要用 `@import "tailwindcss";`，那會把整份 Tailwind CSS 重複輸出到每個檔案。

## 原因

- 各自獨立編譯的 CSS（CSS Module、scoped style）拿不到主 CSS 的 theme 與 utility 定義，`@apply` 會失敗或找不到 class
- `@reference` 只匯入 token 與定義供 `@apply` 解析，不輸出任何實際 CSS
- 用 `@import "tailwindcss"` 會讓每個 scoped 檔案各自打包一份完整 Tailwind，bundle 體積暴增、樣式重複

## ❌ Bad

```css
/* Card.module.css — @import 會在這個檔重複輸出整份 Tailwind */
@import 'tailwindcss';

.card {
  @apply rounded-lg bg-white p-4 shadow;
}
```

## ✅ Good

```css
/* Card.module.css — @reference 只匯入定義供 @apply 解析，不輸出 CSS */
@reference '../app.css';

.card {
  @apply rounded-lg bg-white p-4 shadow;
}
```

若只用到內建 token，可直接 `@reference "tailwindcss";` 省去指向專案 CSS。

## 例外

主 entry CSS 本身（已經 `@import "tailwindcss"` 的那一份）內使用 `@apply` 不需要 `@reference`，因為定義就在同一個編譯範圍內。
