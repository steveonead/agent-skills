---
rule: mocking-avoid-over-mock
category: Mock 與 Spy
tags: [mocking, over-mock, behavior, implementation]
---

# 測行為，避免 over-mock

> 不要把每個相依都 mock 掉、再去斷言「某個內部方法被呼叫了幾次、帶什麼參數」。那是在測實作細節，一重構就壞。只 mock 真正的外部邊界（網路、時間、亂數、檔案系統），其餘讓它實際執行，然後斷言可觀察的回傳值或結果。

## 原因

- 把相依全 mock 掉再斷言內部呼叫，測的是實作而非行為，行為沒變也會因重構而失效
- 判準：若有人改了內部、但函式回傳結果仍正確，這個測試會不會壞？會的話就太貼實作
- AI 傾向 over-mock，明確界定「只 mock 外部邊界」能擋掉大多數脆弱測試

## ❌ Bad

```ts
test('createOrder 計算總額', () => {
  const calcSpy = vi.spyOn(pricing, 'calculate')
  const taxSpy = vi.spyOn(pricing, 'applyTax')

  createOrder(items)

  // 斷言內部方法怎麼被呼叫 → 測實作，重構就壞
  expect(calcSpy).toHaveBeenCalledTimes(1)
  expect(taxSpy).toHaveBeenCalledWith(100)
})
```

## ✅ Good

```ts
test('createOrder 計算含稅總額', () => {
  // 只 mock 外部邊界，例如打 API 取稅率
  vi.spyOn(taxApi, 'getRate').mockResolvedValue(0.08)

  const order = createOrder(items)

  // 斷言可觀察的結果，內部怎麼算不綁死
  expect(order.total).toBe(108)
})
```

內部純函式與同模組的協作對象盡量讓它實際執行；真正需要隔離的是有副作用、不穩定或慢的外部相依。
