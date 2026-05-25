---
rule: utility-apply-avoid
category: Utilities
tags: [utility, apply, component, abstraction]
---

# 不用 @apply 做 UI 抽象，改用 component

> 不要用 `@apply` 把一串 utility 包成 `.btn`、`.card` 之類的語意 class 來做 UI 抽象。重複的 UI 應抽成 React component / Vue SFC。`@apply` 只保留給無法在 markup 加 class 的第三方內容。

## 原因

- 用 `@apply` 抽 class 等於重建一套 CSS 命名系統，失去 utility-first 的初衷，又回到要在 HTML 與 CSS 之間來回對照
- component 能同時封裝結構、行為、狀態與樣式，`@apply` 只能封裝樣式，抽象層次不完整
- `@apply` 抽出的 class 散落在 CSS，重複偵測、tree-shaking、變體支援都不如直接用 utility

## ❌ Bad

```css
/* 用 @apply 重造一套 class，違背 utility-first */
.btn-primary {
  @apply inline-flex items-center rounded-lg bg-blue-500 px-4 py-2 font-medium text-white hover:bg-blue-600;
}
```

## ✅ Good

```tsx
// 重複 UI 抽成 component，封裝結構與樣式
type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement>;

function PrimaryButton({ children, ...props }: ButtonProps) {
  return (
    <button
      className="inline-flex items-center rounded-lg bg-blue-500 px-4 py-2 font-medium text-white hover:bg-blue-600"
      {...props}
    >
      {children}
    </button>
  );
}
```

## 例外

無法掌控、無法加 class 的 markup 才用 `@apply`：

- CMS 或 Markdown 渲染出的 HTML（`.prose` 內的 `<a>`、`<table>`）
- 第三方 widget 注入、無法改 className 的 DOM

```css
/* 第三方 vendor widget 的固定 class，只能用 @apply 套樣式 */
.vendor-tooltip {
  @apply rounded bg-gray-900 px-2 py-1 text-sm text-white;
}
```
