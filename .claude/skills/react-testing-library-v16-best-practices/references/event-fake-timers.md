---
rule: event-fake-timers
category: userEvent 與非同步
tags: [event, userEvent, fake-timers]
---

# 搭配 fake timers 時要傳 advanceTimers

> 用 `vi.useFakeTimers()` 時，`userEvent.setup` 要帶 `advanceTimers: vi.advanceTimersByTime`，否則互動會卡住無法繼續。

## 原因

- userEvent 的互動內部用 delay 排程（輸入字元之間有間隔），fake timers 會凍結時間，delay 永遠到不了，`await` 會一直無法 resolve。
- 把 `advanceTimers` 交給 userEvent，它在等待時會自動推進假時間，互動才能完成。
- 這是 fake timers 與 userEvent 一起用時最常見的「測試卡住不結束」原因，eslint 抓不到。

## ❌ Bad

```ts
vi.useFakeTimers()
const user = userEvent.setup() // 沒接 fake timers
render(<Search />)

await user.type(screen.getByRole('textbox'), 'abc') // 會一直無法 resolve
```

## ✅ Good

```ts
vi.useFakeTimers()
const user = userEvent.setup({
  advanceTimers: vi.advanceTimersByTime, // 互動時自動推進假時間
})
render(<Search />)

await user.type(screen.getByRole('textbox'), 'abc')
vi.advanceTimersByTime(300) // 推進 debounce

expect(await screen.findByRole('listitem')).toBeInTheDocument()
```

測試結束記得 `vi.useRealTimers()` 還原，避免影響其他測試。
