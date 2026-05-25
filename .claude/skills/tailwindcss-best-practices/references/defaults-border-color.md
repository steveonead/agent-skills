---
rule: defaults-border-color
category: 預設行為變更
tags: [defaults, border, breaking-change, migration]
---

# border 預設色從 gray-200 改為 currentColor

> v4 中 `border`、`divide` 等不指定顏色時，預設色從 v3 的 `gray-200` 改為 `currentColor`。原本依賴隱性灰色邊框的元件，升級後邊框會變成文字色，需明確補上顏色 class。

## 原因

- v3 預設灰色邊框是「隱性魔法」，v4 改成 `currentColor` 與原生 CSS 行為一致
- 升級後依賴預設灰邊的卡片、輸入框邊框會默默變成深色（繼承文字色），要人工檢視
- 明確寫出邊框色後行為穩定，不受文字色變動影響

## ❌ Bad

```html
<!-- v3 下是淺灰邊框；v4 下邊框變成 currentColor（通常是深文字色） -->
<div class="border rounded-lg p-4">
  卡片內容
</div>
```

## ✅ Good

```html
<!-- 明確指定邊框色，跨版本行為一致 -->
<div class="border border-gray-200 rounded-lg p-4">
  卡片內容
</div>
```

若要全域維持 v3 行為，可在 base layer 設定預設邊框色：

```css
@layer base {
  *,
  ::after,
  ::before {
    border-color: var(--color-gray-200);
  }
}
```

## 例外

刻意要讓邊框跟隨文字色（例如 icon 周邊的描邊）時，`currentColor` 正是想要的行為，不需額外指定。
