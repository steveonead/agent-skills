---
rule: defaults-ring-width
category: 預設行為變更
tags: [defaults, ring, focus, breaking-change, migration]
---

# ring 預設寬從 3px 改為 1px

> v4 中 `ring`（不帶數字）的預設寬度從 v3 的 `3px` 改為 `1px`。原本靠 `ring` 表示 3px focus 外框的地方，升級後外框會變細，需明確改成 `ring-3`。

## 原因

- v4 調整 `ring` 預設寬度為 `1px`，與 `border` 的直覺一致
- 升級後 focus 外框默默從 3px 縮成 1px，視覺變弱但不報錯，a11y 上的 focus 可見性可能受影響
- focus ring 是無障礙的重要視覺提示，寬度退化要主動處理

## ❌ Bad

```html
<!-- v3 下 ring 是 3px focus 框；v4 下只剩 1px，focus 提示變弱 -->
<button class="focus:ring focus:ring-blue-500">
  送出
</button>
```

## ✅ Good

```html
<!-- 要 3px 外框就明確寫 ring-3 -->
<button class="focus:ring-3 focus:ring-blue-500">
  送出
</button>
```

## 例外

升級後確實想要更細的 1px 外框時，保留 `ring` 即可，不需改 `ring-3`。重點是有意識地選定寬度，而非沿用舊直覺。
