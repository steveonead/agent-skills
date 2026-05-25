---
rule: directive-custom-utility
category: CSS 指令
tags: [directive, utility, layer]
---

# 自訂 utility 改用 @utility，不用 @layer utilities

> 在 v4 定義自家 utility class 改用 `@utility name {}` 指令，不再用 `@layer utilities { .name {} }`。`@utility` 定義的 class 能被變體修飾，且正確參與 v4 的優先級排序。

## 原因

- `@utility` 是 v4 的官方自訂 utility 機制，定義的 class 自動支援 `hover:`、`sm:`、`dark:` 等變體
- 用 `@layer utilities { .foo {} }` 手動塞的 class 不會被當成真正的 utility，變體修飾與優先級行為不如預期
- `@utility` 會依屬性自動排序進正確的 cascade layer，與內建 utility 行為一致

## ❌ Bad

```css
/* 手動塞進 @layer utilities，變體無法套用 */
@layer utilities {
  .content-auto {
    content-visibility: auto;
  }
}
```

## ✅ Good

```css
/* @utility 定義，自動支援 hover:content-auto、md:content-auto 等變體 */
@utility content-auto {
  content-visibility: auto;
}
```

帶參數的 functional utility：

```css
@utility tab-* {
  tab-size: --value(integer);
}
```

## 例外

定義的是元件層級樣式（一整塊 `.card`、`.btn` 視覺）而非單一 utility 時，用 `@layer components` 較合適；但通常更建議直接用 component 封裝（見 `utility-apply-avoid`）。
