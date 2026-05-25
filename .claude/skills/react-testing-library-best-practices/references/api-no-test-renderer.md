---
rule: api-no-test-renderer
category: v16 / React 19 API 變更
tags: [api, react-test-renderer, shallow, deprecated]
---

# 別用 react-test-renderer 或 shallow rendering

> React 19 已 deprecate `react-test-renderer`、移除 `react-test-renderer/shallow`，元件測試一律用 RTL 的 render。

## 原因

- `react-test-renderer` 內建一套不等於使用者環境的 renderer，依賴 React 內部實作，React 19 起標記 deprecated 並只剩 concurrent 行為。
- `react-test-renderer/shallow` 在 React 19 已移除，shallow rendering 會綁死實作細節並擋住升級。
- RTL render 在真實 DOM 環境下測渲染結果，是 React 官方明確點名的取代方案。

## ❌ Bad

```ts
import TestRenderer from 'react-test-renderer' // 已 deprecated

const tree = TestRenderer.create(<Comp />).toJSON()
expect(tree).toMatchSnapshot()
```

## ✅ Good

```ts
import { render, screen } from '@testing-library/react'

render(<Comp />)
expect(screen.getByRole('heading', { name: /標題/ })).toBeInTheDocument()
```

需要 snapshot 時可用 render 回傳的 `asFragment()`，但優先斷言可見行為而非整棵元件樹。
