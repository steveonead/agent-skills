---
rule: config-source-path
category: 設定方式
tags: [config, source, path]
---

# @source 路徑相對於 CSS 檔案位置，不是專案根目錄

> `@source` 的相對路徑以「該 CSS 檔案所在目錄」為基準解析，不是專案根目錄。寫路徑前先確認 CSS 檔在哪一層。

## 原因

- v3 的 `content` glob 以專案根目錄為基準，沿用同樣的直覺寫 `@source` 會指錯位置
- 指錯路徑時 Tailwind 掃不到 class，畫面樣式默默消失，且沒有明顯錯誤訊息，排查成本高
- CSS 檔常放在 `src/styles/` 之類的子目錄，相對路徑要往上跳幾層必須算清楚

## ❌ Bad

```css
/* src/styles/app.css — 誤以為相對於專案根目錄 */
@import 'tailwindcss';

/* 實際解析成 src/styles/components/，路徑錯誤 */
@source './components';
```

## ✅ Good

```css
/* src/styles/app.css — 相對於本檔所在的 src/styles/ */
@import 'tailwindcss';

/* 要指到 src/components/，需往上跳一層 */
@source '../components';
```

## 例外

想避免相對路徑的歧義時，可用以 `@source` 搭配從專案根目錄起算的絕對 glob（前綴 `/`），路徑會相對於專案根目錄解析。
