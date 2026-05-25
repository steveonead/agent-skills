---
rule: directive-variants
category: CSS 指令
tags: [directive, variants, responsive, removed]
---

# @variants、@responsive 已移除，直接用 utility 或 @layer

> v4 移除了 `@variants` 與 `@responsive` 指令。需要套用變體時直接在 markup 用變體 class，需要在 CSS 定義可被變體修飾的 class 時放進對應的 `@layer`。

## 原因

- `@variants` 與 `@responsive` 在 v4 已不存在，沿用會編譯錯誤
- v4 中放進 `@layer` 的 class 本來就能被 `hover:`、`sm:` 等變體修飾，不需要額外指令包裹
- 大部分用 `@responsive` 包的東西，原本就該回到 markup 直接用變體

## ❌ Bad

```css
/* v4 已移除這兩個指令 */
@responsive {
  .card {
    padding: 2rem;
  }
}

@variants hover, focus {
  .btn-active {
    background: blue;
  }
}
```

## ✅ Good

```html
<!-- 變體直接寫在 markup -->
<div class="p-4 sm:p-8">...</div>
<button class="hover:bg-blue-600 focus:bg-blue-700">...</button>
```

若真要在 CSS 自訂可被變體修飾的 utility，改用 `@utility`：

```css
@utility card {
  padding: 2rem;
}
```

`card` 自動可被 `sm:card`、`hover:card` 等變體修飾。

## 例外

無，這兩個指令在 v4 完全移除，沒有相容寫法。
