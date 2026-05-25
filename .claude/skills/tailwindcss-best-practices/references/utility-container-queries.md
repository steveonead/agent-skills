---
rule: utility-container-queries
category: Utilities
tags: [utility, container-query, responsive, reusable]
---

# 可複用元件用 @container 容器變體，不用 viewport breakpoint

> 可複用元件的內部 responsive 改用 v4 內建的 container query：父層加 `@container`，子層用 `@sm:`、`@md:` 等容器變體。元件依「自己所在容器的寬度」調整，而非整個 viewport。viewport breakpoint（`sm:`、`md:`）保留給 app-level layout。

## 原因

- 同一個卡片元件可能出現在寬 sidebar、窄 main、grid cell，依 viewport 調整會錯判，依容器寬度才正確
- v4 把 container query 內建，不再需要 `@tailwindcss/container-queries` 插件
- 元件變得自足：搬到任何容器都能正確 reflow，不必知道頁面 layout

## ❌ Bad

```html
<!-- 卡片依 viewport 調整，放進窄 sidebar 時版面會錯 -->
<article class="flex flex-col md:flex-row">
  <img class="w-full md:w-1/3" />
  <div class="p-4">...</div>
</article>
```

## ✅ Good

```html
<!-- 父層宣告 container，卡片依容器寬度 reflow -->
<div class="@container">
  <article class="flex flex-col @md:flex-row">
    <img class="w-full @md:w-1/3" />
    <div class="p-4">...</div>
  </article>
</div>
```

## 例外

整頁的 app-level layout（頁首、主側欄收合、整體欄數）本質上就是依 viewport 決定，用 `sm:`、`lg:` 等 viewport breakpoint 才對。container query 是給「容器內可複用元件」，不是取代所有 viewport 斷點。
