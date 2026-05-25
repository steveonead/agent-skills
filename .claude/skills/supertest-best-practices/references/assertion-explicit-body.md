---
rule: assertion-explicit-body
category: 斷言
tags: [assertion, response-body, coverage]
---

# 不要只斷言 status，要驗 body 結構

> 只檢查 status code 的 e2e 測試保護力很弱，要明確斷言 response body 的關鍵欄位與結構，確認回的是對的資料。

## 原因

- 一個 endpoint 回 200 但 body 完全錯（欄位漏了、值算錯、結構變了）是很常見的 regression，只看 status 完全抓不到。
- 明確斷言 body 等於把「這個 API 該回什麼」寫進測試，後人改動 response 形狀時測試會立刻反映，這正是 e2e 測試的價值。
- 用 `toMatchObject` 斷言關鍵欄位，比起逐欄位 `toBe` 更穩健，也不會因為多了無關欄位就誤判。

## ❌ Bad

```ts
it('GET /orders/:id', async () => {
  await request(app.getHttpServer())
    .get('/orders/order-1')
    .expect(200); // 只確認回 200，body 是空物件、欄位算錯都測不出來
});
```

只把關 status，endpoint 回了 200 卻回傳錯誤資料時測試照樣綠燈，等於沒驗到核心行為。

## ✅ Good

```ts
import { expect } from 'vitest';

it('GET /orders/:id', async () => {
  const res = await request(app.getHttpServer())
    .get('/orders/order-1')
    .expect(200);

  expect(res.body).toMatchObject({
    id: 'order-1',
    status: 'confirmed',
    items: expect.arrayContaining([
      expect.objectContaining({ productId: 'item-1' }),
    ]),
  });
});
```

明確驗證 body 的關鍵欄位與結構，把 API 的回應契約寫進測試。response 形狀一旦被改壞，測試立刻失敗。

## 補充

- 結構穩定、欄位固定的回應，也可用 supertest 的 `.expect(200, { ... })` 一次斷言 status 加完整 body。
- 兩個 `expect` 的分工見 `assertion-supertest-vs-vitest`。
