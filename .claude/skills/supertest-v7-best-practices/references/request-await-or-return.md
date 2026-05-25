---
rule: request-await-or-return
category: 請求撰寫
tags: [request, async, await, flaky]
---

# 每個 request 一定要 await 或 return

> supertest 的 request chain 是 thenable，要嘛 `await` 它、要嘛從 test 把它 `return`，否則斷言不會被等到，測試會假性通過。

## 原因

- `.expect()` 與實際送請求都是非同步的，沒被 await 或 return 的 chain，test function 會在請求完成前就結束，Vitest 判定通過。
- 這種測試最危險的地方在於它「永遠綠燈」，連 endpoint 整個壞掉都測不出來，等於沒測。
- 漏掉的 request 還可能在 test 結束後才完成，造成跨 test 的 race 與不穩定。

## ❌ Bad

```ts
it('GET /cats', () => {
  request(app.getHttpServer())
    .get('/cats')
    .expect(200); // 沒有 await 也沒有 return，斷言根本沒被等到
});
```

chain 既沒 await 也沒 return，test 在請求送出前就結束，回傳 500 也一樣顯示通過。

## ✅ Good

```ts
// 寫法一：async / await
it('GET /cats', async () => {
  await request(app.getHttpServer())
    .get('/cats')
    .expect(200);
});

// 寫法二：直接 return chain
it('GET /cats', () => {
  return request(app.getHttpServer())
    .get('/cats')
    .expect(200);
});
```

兩種寫法都能讓 Vitest 等到請求與斷言真正完成。團隊內挑一種風格統一即可，多數情況用 `async` / `await` 最直覺。

## 補充

- 取得 response 物件再做 Vitest 斷言時，更要 await，見 `assertion-supertest-vs-vitest`。
- 這條與測試框架無關，是 supertest chain 本身的 thenable 特性。
