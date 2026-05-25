---
rule: security-sanitize-html
category: 安全性
tags: [security, xss, dangerouslySetInnerHTML]
---

# dangerouslySetInnerHTML 必須消毒

> 任何傳入 `dangerouslySetInnerHTML` 的 HTML 字串必須先經過 DOMPurify 消毒，即使資料來自自己的 API。使用者提供的 URL 在 `href` / `src` 必須先驗證 scheme。

## 原因

- React 預設會 escape JSX 中的字串，`dangerouslySetInnerHTML` 是繞過這層保護的後門
- 自家 API 也可能被入侵、DB 可能被注入、第三方資料來源可能有惡意內容，零信任
- `javascript:` scheme 的 URL 可以在 `href` / `src` 中執行任意程式碼

## ❌ Bad

```tsx
// 未消毒，XSS 風險
function RichContent({ html }: { html: string }) {
  return <div dangerouslySetInnerHTML={{ __html: html }} />;
}

// 未驗證 URL,javascript: 注入風險
function UserLink({ url }: { url: string }) {
  return <a href={url}>Visit</a>;
}
```

## ✅ Good

```tsx
import DOMPurify from 'dompurify';

function RichContent({ html }: { html: string }) {
  const clean = DOMPurify.sanitize(html);
  return <div dangerouslySetInnerHTML={{ __html: clean }} />;
}

function SafeLink({ url, children }: { url: string; children: React.ReactNode }) {
  const safeUrl = /^https?:\/\//.test(url) ? url : '#';
  return <a href={safeUrl} rel="noopener noreferrer">{children}</a>;
}
```

## 關鍵原則

- 任何包含 `dangerouslySetInnerHTML` 的 PR 都必須追溯資料來源並確認有消毒
- 優先用「結構化資料 + 元件 render」表達內容（例如把 markdown 解析成 AST 後用元件 render），避免直接吃 raw HTML
- 消毒在**輸出時**做，不在輸入時，因為 DOMPurify 的規則會更新
- 外部 URL 的 `<a>` 一律加上 `rel="noopener noreferrer"`

## 同類危險場景

- `iframe` 的 `src` 接受使用者輸入 → 同樣需要驗 scheme + sandbox
- `img` 的 `src` 接受使用者輸入 → 驗 scheme，避免 `data:` 或 `javascript:`
- 把使用者輸入塞進 inline `<style>` 或 `<script>` → 直接禁用
