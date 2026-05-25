---
name: tailwindcss-v4-best-practices
description: TailwindCSS v4 最佳實踐規則集，供撰寫、審查或重構 TailwindCSS v4 相關程式碼時參考。明確要求使用 v4 的 CSS-first 設定方式，避免回退到 v3 的 JS config 寫法。適用於新功能開發、PR self-review、v3 → v4 migration。不適用於 TailwindCSS v3 專案，也不重複 `eslint-plugin-better-tailwindcss` 已能自動處理的 class 重新命名與排序檢查。
---

# TailwindCSS v4 Best Practices

針對 TailwindCSS v4 的 CSS-first 架構，整理出讓 agent 寫出正確 v4 語法、不回退到 v3 寫法的高 ROI 規則。專注於設定方式、CSS 指令、design token、預設行為變更與 utility 抽象策略，不重複 `eslint-plugin-better-tailwindcss` 已能完全覆蓋的 class 重新命名與排序檢查。

## 適用時機

參考這份規則集的時機：
- 撰寫新的 TailwindCSS v4 樣式或設定
- 審查 PR 中的 Tailwind 相關程式碼品質
- 將 TailwindCSS v3 專案 migration 到 v4
- 排查 v4 升級後出現的非預期視覺差異或樣式失效

## 規則分類

| 分類 | 前綴 |
|------|------|
| 設定方式 | `config-` |
| CSS 指令 | `directive-` |
| Design Tokens | `token-` |
| 預設行為變更 | `defaults-` |
| Utilities | `utility-` |

## 規則速查

### 設定方式

- `config-no-js` — 自訂 theme 改用 CSS `@theme {}`，不用 `tailwind.config.js` 的 `theme.extend`
- `config-no-content` — 不再設定 `content` 陣列，需額外掃描的路徑用 `@source` 指定
- `config-source-path` — `@source` 路徑相對於 CSS 檔案位置，不是專案根目錄
- `config-plugins` — 插件改用 `@plugin "package-name"` CSS 指令，不在 JS config `require()`
- `config-gitignore` — v4 自動偵測預設尊重 `.gitignore`，外部 template 需手動加 `@source`

### CSS 指令

- `directive-screen` — `@screen sm {}` 已移除，改用 `@media screen(sm) {}`
- `directive-variants` — `@variants`、`@responsive` 已移除，直接用 utility class 或 `@layer`
- `directive-apply-reference` — scoped CSS 中用 `@apply` 需先加 `@reference`，不用 `@import`
- `directive-custom-utility` — 自訂 utility 改用 `@utility` 指令，不用 `@layer utilities`

### Design Tokens

- `token-css-vars` — 用 `var(--color-blue-500)` 取代 `theme('colors.blue.500')`
- `token-theme-inline` — `@theme inline` 固化值，執行期主題切換會失效
- `token-theme-vs-root` — 需生成 utility 的 token 放 `@theme`，純執行期變數放 `:root`
- `token-prefer-default` — 優先用內建 design token，任意值是逃生艙不是替代品

### 預設行為變更

- `defaults-border-color` — `border` 預設色從 `gray-200` 改為 `currentColor`
- `defaults-ring-width` — `ring` 預設寬從 `3px` 改為 `1px`
- `defaults-shadow-scale` — shadow / blur scale 整體位移，需人工驗收

### Utilities

- `utility-apply-avoid` — 不用 `@apply` 做 UI 抽象，改用 component
- `utility-container-queries` — 可複用元件用 `@container` 容器變體，不用 viewport breakpoint
- `utility-layer-unlayered` — 未放進 `@layer` 的 CSS 優先級最高，第三方 CSS 要包進 `@layer`

## 使用方式

讀取個別規則檔案以取得詳細說明與範例：

```
references/<類別前綴>-<規則名稱>.md
```

每個規則檔案包含：
- 說明此規則重要的原因
- `❌ Bad` 反例與 `✅ Good` 正確寫法
- 例外情況（若有白名單）
- 延伸參考連結（若有）
