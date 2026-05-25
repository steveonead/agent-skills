---
rule: token-theme-vs-root
category: Design Tokens
tags: [token, theme, root, utility-generation]
---

# 需生成 utility 的 token 放 @theme，純執行期變數放 :root

> 判斷變數該放哪：需要 Tailwind 生成對應 utility class（`bg-*`、`text-*`、`p-*`）的 token 放 `@theme`；只在 CSS 內部用 `var()` 取用、不需要任何 utility 的變數放 `:root`。

## 原因

- `@theme` 內每個 token 都會生成一整組 utility，放了不需要 utility 的變數會產生用不到的 class，污染 autocomplete 與輸出
- `:root` 內的變數純粹是 CSS 自訂屬性，不觸發 utility 生成，適合元件內部尺寸、z-index 層級之類的私有值
- 分清楚兩者，theme 保持為「設計系統公開 token」，`:root` 為「實作細節變數」

## ❌ Bad

```css
@theme {
  --color-primary: #3b82f6;
  /* 只在某元件內部用一次的私有值，不該生成一整組 utility */
  --modal-z-index: 50;
  --sidebar-internal-gap: 12px;
}
```

## ✅ Good

```css
@theme {
  /* 需要 bg-primary / text-primary 等 utility */
  --color-primary: #3b82f6;
}

:root {
  /* 純內部用，不需要 utility */
  --modal-z-index: 50;
  --sidebar-internal-gap: 12px;
}
```

## 例外

無。判斷標準很單純：會用到 `xxx-token` 形式的 utility 就放 `@theme`，否則放 `:root`。
