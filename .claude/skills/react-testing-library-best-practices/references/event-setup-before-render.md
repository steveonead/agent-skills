---
rule: event-setup-before-render
category: userEvent 與非同步
tags: [event, userEvent, setup]
---

# userEvent.setup() 在 render 前建立並複用

> 每個測試先 `const user = userEvent.setup()` 再 render，整個測試共用同一個 user 實例，不要每次互動都重新 setup。

## 原因

- userEvent v14 起的互動方法是非同步、且綁在 `setup()` 回傳的實例上，`setup()` 會配置 clipboard、pointer 等狀態，重複 setup 會把這些狀態重新初始化。
- 在 render 之前 setup，能確保互動 API 在元件掛載前就準備好，行為一致。
- 自動化檢查多半只要求「用 userEvent 而非 fireEvent」，不管有沒有正確 setup 與複用，所以這條要自己守。

## ❌ Bad

```ts
test('送出表單', async () => {
  render(<Form />)
  await userEvent.click(screen.getByRole('button')) // 直接用 static API，沒 setup
  await userEvent.type(screen.getByRole('textbox'), 'hi') // 又走一次預設實例
})
```

## ✅ Good

```ts
test('送出表單', async () => {
  const user = userEvent.setup() // render 前建立
  render(<Form />)

  await user.type(screen.getByRole('textbox', { name: /名稱/ }), 'hi')
  await user.click(screen.getByRole('button', { name: /送出/ }))
})
```

常見做法是包一個 setup helper 同時回傳 user 與 render 結果，跨測試重用同一個模式。
