---
rule: defaults-shadow-scale
category: 預設行為變更
tags: [defaults, shadow, blur, scale, breaking-change, migration]
---

# shadow / blur scale 整體位移，需人工驗收

> v4 重新命名了 shadow、blur、radius 等 scale，整體往上位移。例如 v3 的 `shadow-sm` 在 v4 對應 `shadow-xs`、v3 的 `shadow` 對應 `shadow-sm`。沿用舊 class 名稱不會報錯，但視覺會比 v3 更重。ESLint 抓不到，必須人工驗收。

## 原因

- v4 把原本沒有 `xs` 級距的 scale 補上，導致中間級距整體往大的方向位移
- class 名稱在兩版都合法，升級後不報錯，但同一個 `shadow-sm` 視覺從「很淡」變成「較明顯」
- 同樣位移也發生在 `blur`、`rounded` 等 scale，畫面細節默默改變

## 對應關係（節錄）

| v3 | v4 |
|---|---|
| `shadow-sm` | `shadow-xs` |
| `shadow` | `shadow-sm` |
| `blur-sm` | `blur-xs` |
| `blur` | `blur-sm` |
| `rounded-sm` | `rounded-xs` |
| `rounded` | `rounded-sm` |

## ❌ Bad

```html
<!-- migration 後沿用 v3 名稱，視覺比原本更重 -->
<div class="shadow-sm blur-sm rounded">...</div>
```

## ✅ Good

```html
<!-- 想維持 v3 的淡陰影，降一級到 xs -->
<div class="shadow-xs blur-xs rounded-sm">...</div>
```

## 驗收義務

這類位移無法靠工具偵測，migration 後必須：

- 逐頁人工比對升級前後的陰影、圓角、模糊視覺
- 對設計稿敏感的關鍵頁面截圖比對
- 確認後再決定保留新視覺或降級回原本級距
