---
rule: api-act-import
category: v16 / React 19 API 變更
tags: [api, act, react19, breaking-change]
---

# act 從 react import，別用 react-dom/test-utils

> React 19 把 act 移到 `react`，act 要從 `react` 取得；`react-dom/test-utils` 的 act 已 deprecated，多數情況用 RTL 重新導出的 act 即可。

## 原因

- React 19 把 act 移到 `react` 套件，`react-dom/test-utils` 的 act 變成 deprecated alias，沿用舊路徑只會跳 deprecation warning；而 `Simulate`、`renderIntoDocument` 等其他 test-utils 函式才是被移除、呼叫即拋出錯誤。
- act 的正確來源從 React 18 起就是 `react` 套件本身，RTL v16 內部也優先採用 `React.act`。
- RTL 已把 render 與 fireEvent 包在 act 裡，手動 act 多半不必要，真要用時務必從正確來源拿。

## ❌ Bad

```ts
import { act } from 'react-dom/test-utils' // React 19 起 deprecated，會跳 deprecation warning
```

## ✅ Good

```ts
import { act } from 'react' // 正確來源
// 或直接用 RTL 重新導出的版本
import { act } from '@testing-library/react'
```

只有在需要手動觸發更新（例如測 hook 內部的 state 變化）時才用 act，並用它包住會造成 state 更新的呼叫。
