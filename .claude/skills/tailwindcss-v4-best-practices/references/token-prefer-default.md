---
rule: token-prefer-default
category: Design Tokens
tags: [token, arbitrary-value, design-system]
---

# 優先用內建 design token，任意值是逃生艙不是替代品

> 排版、間距、顏色優先用內建 design token（`text-base`、`p-4`、`text-blue-500`），避免任意值（`text-[16px]`、`p-[16px]`、`text-[#3b82f6]`）。任意值是 design token 不足時的逃生艙，不是日常替代品。

## 原因

- 內建 token 來自統一的 scale，保證間距、字級節奏一致，任意值會讓設計系統碎裂
- 任意值繞過 theme，無法被主題切換或全域調整影響，日後改設計要逐處手改
- 同一個 `16px` 散落成 `p-[16px]`、`p-4`、`p-[1rem]` 多種寫法，可讀性與一致性都差

## ❌ Bad

```html
<!-- 任意值繞過 design token，數字硬寫 -->
<div class="p-[16px] text-[16px] text-[#3b82f6]">...</div>
```

## ✅ Good

```html
<!-- 用內建 token，與設計系統 scale 對齊 -->
<div class="p-4 text-base text-blue-500">...</div>
```

scale 真的缺值時，先在 `@theme` 補 token，而非散落任意值：

```css
@theme {
  --spacing-18: 4.5rem; /* 補進 scale，之後用 p-18 */
}
```

## 例外

一次性、不會重複的精確值（例如對齊某張背景圖的 `top-[117px]`、第三方元件要求的特定尺寸）可用任意值，這正是逃生艙的用途。
