---
rule: config-plugins
category: 設定方式
tags: [config, plugin, css-first]
---

# 插件改用 @plugin CSS 指令，不在 JS config require()

> 載入 Tailwind 插件（如 `@tailwindcss/typography`、`@tailwindcss/forms`）改用 CSS 的 `@plugin "package-name"`，不再寫 JS config 的 `plugins: [require(...)]`。

## 原因

- v4 預設不讀 `tailwind.config.js`，舊的 `plugins` 陣列寫了也不會生效
- `@plugin` 與其他 CSS-first 設定同檔，插件、theme、source 一目了然
- 插件選項可直接在 CSS 指令後接設定，不必繞 JS

## ❌ Bad

```js
// tailwind.config.js
export default {
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
  ],
};
```

## ✅ Good

```css
/* app.css */
@import 'tailwindcss';

@plugin '@tailwindcss/typography';
@plugin '@tailwindcss/forms';
```

需要傳選項時：

```css
@plugin '@tailwindcss/forms' {
  strategy: class;
}
```

## 例外

插件本身尚未支援 v4、只提供 JS 形式時，可暫時用 `@config` 載入含 `plugins` 的舊 config 作為過渡。
