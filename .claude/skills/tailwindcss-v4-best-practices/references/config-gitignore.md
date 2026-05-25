---
rule: config-gitignore
category: 設定方式
tags: [config, source, gitignore, detection]
---

# 自動偵測尊重 .gitignore，外部 template 需手動加 @source

> v4 的自動 content detection 預設會跳過 `.gitignore` 內的檔案。若有被 git 忽略、但仍含 Tailwind class 的 template（例如 Rails、Django 產生在 ignore 目錄的檔案），需用 `@source` 手動指定。

## 原因

- 自動偵測為了效能與正確性，會排除 `node_modules` 與 `.gitignore` 列出的路徑
- 後端框架常把產生的 view 放在被 git 忽略的目錄，這些檔的 class 會掃不到，畫面樣式默默消失
- 用 `@source` 顯式指定後，Tailwind 會強制掃描該路徑，覆蓋 `.gitignore` 的排除

## ❌ Bad

```css
/* app.css — 倚賴自動偵測，但 view 目錄被 .gitignore 排除 */
@import 'tailwindcss';

/* Rails/Django 產生的 template 在被忽略的目錄，class 全部掃不到 */
```

## ✅ Good

```css
/* app.css — 顯式補上被 .gitignore 排除但含 class 的來源 */
@import 'tailwindcss';

@source '../app/views';
@source '../templates';
```

## 例外

被忽略的目錄確實不含任何 Tailwind class（純資料、build 產物）時，不需要也不應該加 `@source`，以免拖慢掃描。
