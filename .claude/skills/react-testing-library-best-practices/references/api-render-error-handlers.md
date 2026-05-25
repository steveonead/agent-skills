---
rule: api-render-error-handlers
category: v16 / React 19 API 變更
tags: [api, render, error-handling, react19, breaking-change]
---

# onUncaughtError 已移除，改用 onCaughtError / onRecoverableError

> v16 拿掉了 render 的 `onUncaughtError` option，render 現在對未捕捉錯誤直接 throw；React 19 改提供 `onCaughtError` 與 `onRecoverableError`。

## 原因

- 舊的 `onUncaughtError` 不再支援，未被 Error Boundary 捕捉的錯誤會由 render 直接拋出，讓測試自然失敗。
- React 19 對齊 `createRoot` 的錯誤回呼：`onCaughtError`（被 Error Boundary 接住的錯誤）與 `onRecoverableError`（自動回復的錯誤）。
- 想斷言「元件拋錯被 boundary 接住」時，用 `onCaughtError` 搭配一個當 boundary 的 wrapper，而不是沿用已移除的 option。

## ❌ Bad

```ts
render(<Broken />, {
  onUncaughtError: (e) => {
    /* ... */
  }, // v16 已不支援
})
```

## ✅ Good

```ts
const onCaughtError = vi.fn()

// ErrorBoundary 需實作 getDerivedStateFromError / componentDidCatch
render(
  <ErrorBoundary>
    <Broken />
  </ErrorBoundary>,
  { onCaughtError },
)

expect(onCaughtError).toHaveBeenCalled()
```

未被接住的錯誤不必自己掛 handler，render 會直接 throw 讓測試 fail。
