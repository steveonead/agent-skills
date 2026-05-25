---
rule: query-byrole-name
category: query 用法
tags: [query, getByRole, name]
---

# getByRole 用 { name } 精準鎖定

> 同一個 role 有多個時，用 getByRole 的 `{ name }` option 以 accessible name 鎖定，別退回 getByText 或 testId。

這條只談 `{ name }` 這個框架 API 用法，不論述「為何優先用 role」的 query 優先序哲學。

## 原因

- 頁面常有多個同 role 元素（多顆 button、多個 textbox），單用 `getByRole('button')` 會因為多筆而 throw。
- `{ name }` 比對的是 accessible name（按鈕文字、`aria-label`、表單 label 等），語意明確且貼近使用者辨識元素的方式。
- 用正則加忽略大小寫（`/送出/i`）比對，文字大小寫或前後空白變動時不會誤判。

## ❌ Bad

```tsx
// 畫面上有「儲存」和「送出」兩顆 button
screen.getByRole('button') // 多筆，直接 throw
screen.getByText('送出') // 退回文字查詢，較脆弱
```

## ✅ Good

```tsx
screen.getByRole('button', { name: /送出/i })
screen.getByRole('textbox', { name: /電子郵件/i })
screen.getByRole('heading', { level: 2, name: /結帳/i })
```

`{ name }` 接受字串或正則，多數情況用忽略大小寫的正則最不易失效。
