---
rule: config-no-content
category: 設定方式
tags: [config, content, source, detection]
---

# 不再設定 content 陣列，額外掃描路徑用 @source 指定

> v4 自動偵測專案內的 template 檔案，不再需要手動維護 `content` 陣列。預設掃描不到的路徑（例如套件內的元件、monorepo 其他 package）用 CSS 的 `@source` 指令補上。

## 原因

- v4 內建自動 content detection，會掃描專案檔案並自動排除 `node_modules` 與 `.gitignore` 內容
- 手寫 `content` glob 容易漏路徑或寫錯，class 沒被掃到就不會生成，畫面默默壞掉
- `@source` 與 CSS 設定同檔，新增掃描來源時不必跳到 JS config

## ❌ Bad

```js
// tailwind.config.js
export default {
  content: [
    './src/**/*.{js,ts,jsx,tsx}',
    './node_modules/@my-org/ui/**/*.{js,ts}',
  ],
};
```

## ✅ Good

```css
/* app.css */
@import 'tailwindcss';

/* 專案內檔案自動偵測，無須設定。只補上預設掃不到的外部來源 */
@source '../node_modules/@my-org/ui';
```

## 例外

完全沒有額外來源時，連 `@source` 都不用寫，只保留 `@import 'tailwindcss';` 即可。
