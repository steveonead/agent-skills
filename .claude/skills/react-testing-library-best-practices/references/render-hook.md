---
rule: render-hook
category: render 進階用法
tags: [render, renderHook, hooks]
---

# 測 custom hook 用 renderHook 與 result.current

> 用 `renderHook` 測 hook，透過 `result.current` 讀最新值，會改 state 的呼叫包在 `act` 裡。

## 原因

- `renderHook` 把 hook 放進一個極小的測試元件執行，讓你不必為了測 hook 額外寫一個假元件。
- `result.current` 永遠指向「最後一次 render 的值」，要拿更新後的值就重讀 `result.current`，別把它解構成區域變數後一直用舊的。
- 觸發 state 更新（呼叫 hook 回傳的 setter 或 action）要包 `act`，確保 React 跑完 re-render 再斷言。

## ❌ Bad

```ts
const { result } = renderHook(() => useCounter())
const { count, increment } = result.current // 解構出舊值

increment() // 沒包 act，且 count 還是舊的
expect(count).toBe(1) // 永遠看不到更新
```

## ✅ Good

```ts
import { act, renderHook } from '@testing-library/react'

const { result } = renderHook(() => useCounter())

act(() => {
  result.current.increment() // 會改 state，包在 act 裡
})

expect(result.current.count).toBe(1) // 重讀 result.current 拿最新值
```

要測 hook 對 props 變化的反應，搭配 `renderHook` 的 `initialProps` 與回傳的 `rerender`。
