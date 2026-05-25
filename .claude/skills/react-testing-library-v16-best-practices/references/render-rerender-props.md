---
rule: render-rerender-props
category: render 進階用法
tags: [render, rerender, props]
---

# 測 prop 更新用 rerender，不要重新 render

> 要驗證「props 改變後元件如何反應」，用 render 回傳的 `rerender` 更新同一棵樹，而不是再呼叫一次 render。

## 原因

- 再呼叫一次 render 會掛載一個全新實例，原本的還留著（除非 cleanup），畫面上同時存在兩份，query 容易撞到多筆。
- `rerender` 沿用同一個 root，能真實重現 React 在 props 變化時的 re-render 與 effect 行為。
- 這是測 `memo`、`useEffect` 依賴、受控元件更新時的正確手法。

## ❌ Bad

```tsx
const { getByText } = render(<Badge count={1} />)
expect(getByText('1')).toBeInTheDocument()

render(<Badge count={2} />) // 又掛一個新實例，畫面上有兩個 Badge
expect(getByText('2')).toBeInTheDocument()
```

## ✅ Good

```tsx
const { rerender } = render(<Badge count={1} />)
expect(screen.getByText('1')).toBeInTheDocument()

rerender(<Badge count={2} />) // 更新同一棵樹
expect(screen.getByText('2')).toBeInTheDocument()
```

`rerender` 傳入完整的新 element，React 會對同一個 root 做 reconcile。
