---
rule: api-render-legacyroot
category: v16 / React 19 API 變更
tags: [api, render, legacyRoot, react19, breaking-change]
---

# 不要再用 legacyRoot render option

> `legacyRoot` 在 React 19 會拋出錯誤，React 18 / 19 都走 concurrent `createRoot`，沒有退回舊 `ReactDOM.render` 的選項。

## 原因

- `legacyRoot: true` 以前用來強制走 React 18 之前的同步 `ReactDOM.render`，但 React 19 已移除該 API，傳這個 option 會 throw。
- 即使在 React 18，`legacyRoot` 也只是觸發 deprecation warning，不是該長期依賴的選項。
- 測試環境應與 production 一致，production 早已是 `createRoot`，測試沒有理由還跑 legacy 模式。

## ❌ Bad

```ts
render(<App />, { legacyRoot: true }) // React 19 會拋出錯誤
```

## ✅ Good

```ts
render(<App />) // 預設就是 concurrent root，與 production 一致
```

若舊測試是為了繞過某個 concurrent 行為才開 `legacyRoot`，正解是修測試或元件本身，而不是退回 legacy。
