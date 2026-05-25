---
rule: timers-fake
category: Fake Timer
tags: [timers, useFakeTimers, advanceTimersByTime, useRealTimers]
---

# Fake timer 用完一定要還原

> 測試 `setTimeout` / `setInterval` / `Date` 相關邏輯時，用 `vi.useFakeTimers()` 接管時間，再用 `vi.advanceTimersByTime()` 推進。每個測試結束務必 `vi.useRealTimers()` 還原，否則 fake timer 會污染後續測試。

## 原因

- fake timer 是全域狀態，沒還原會讓後面的測試卡在假時間、出現難解的逾時
- `advanceTimersByTime` 讓時間「快轉」，不必真的等待，測試更快也更穩定
- 不用真實 `await sleep` 等時間流逝，避免 flaky 與不必要的延遲

## ❌ Bad

```ts
test('debounce fires once', () => {
  vi.useFakeTimers()
  const fn = vi.fn()
  const debounced = debounce(fn, 200)
  debounced()
  vi.advanceTimersByTime(200)
  expect(fn).toHaveBeenCalledTimes(1)
  // 沒還原 → 下一個測試還在 fake time
})
```

## ✅ Good

```ts
beforeEach(() => {
  vi.useFakeTimers()
})

afterEach(() => {
  vi.useRealTimers()
})

test('debounce fires once', () => {
  const fn = vi.fn()
  const debounced = debounce(fn, 200)
  debounced()
  vi.advanceTimersByTime(200)
  expect(fn).toHaveBeenCalledTimes(1)
})
```

需要固定「現在時間」時，用 `vi.setSystemTime(new Date('2026-01-01'))`，同樣記得在 `afterEach` 還原。
