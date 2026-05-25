---
rule: utility-layer-unlayered
category: Utilities
tags: [utility, cascade-layer, specificity, third-party]
---

# 未放進 @layer 的 CSS 優先級最高，第三方 CSS 要包進 @layer

> v4 用原生 CSS cascade layers 管理優先級。任何沒被放進 `@layer` 的 CSS，優先級高於所有在 layer 內的規則（包含全部 Tailwind utility），會無聲蓋過 utility。第三方 CSS、legacy stylesheet 匯入時要用 `@layer` 包起來。

## 原因

- CSS 規範中，unlayered 樣式的優先級高於任何 layered 樣式，與 specificity 數值無關
- 直接 `@import "some-library.css"`（未指定 layer）會讓整份第三方樣式凌駕 Tailwind，utility 改不動畫面
- 把第三方 CSS 放進 `@layer`（如 `components`）後，它就受 layer 順序約束，utility 能正常覆蓋

## ❌ Bad

```css
@import 'tailwindcss';

/* 未指定 layer，整份第三方 CSS 優先級最高，蓋過所有 utility */
@import 'some-ui-library/dist/style.css';
```

## ✅ Good

```css
@import 'tailwindcss';

/* 包進 layer，受 cascade 順序約束，utility 可正常覆蓋 */
@import 'some-ui-library/dist/style.css' layer(components);
```

無法用 `@import ... layer()` 時，包一層 `@layer` 區塊：

```css
@layer components {
  /* legacy stylesheet 內容 */
}
```

## 例外

確實需要某段樣式以最高優先級存在、刻意要蓋過所有 utility（極少數第三方覆寫場景）時，才保留 unlayered。這應是有意識的決定，並加註解說明，而非匯入時的疏忽。
