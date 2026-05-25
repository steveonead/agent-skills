---
rule: assertion-supertest-vs-vitest
category: 斷言
tags: [assertion, expect, vitest, supertest]
---

# 分清 supertest 的 .expect() 與 Vitest 的 expect()

> 兩個 `expect` 來源不同：supertest 的 `.expect()` 鏈在 request 上、由 superagent 提供；Vitest 的 `expect()` 是 matcher。用 supertest 的 `.expect()` 做請求層級前置檢查，用 Vitest `expect()` 驗證 body 細節。

## 原因

- supertest 的 `.expect(200)`、`.expect('Content-Type', /json/)` 是請求成功與否的「門檻」，失敗時直接 reject，語意是「這個請求根本沒按預期回來」。
- Vitest 的 `expect(res.body).toMatchObject(...)` 提供豐富 matcher 與清楚的 diff 錯誤訊息，適合驗證 response body 的結構與欄位。
- 把 status 也硬塞進 Vitest（先 await 再 `expect(res.status).toBe(200)`），會讓 supertest 的鏈式前置檢查形同虛設，也讓「請求失敗」和「資料不符」兩種錯誤混在一起難以區分。

## ❌ Bad

```ts
import { expect } from 'vitest';

it('POST /orders', async () => {
  const res = await request(app.getHttpServer())
    .post('/orders')
    .send(dto);

  // 全部用 Vitest expect，status 檢查淹沒在資料斷言裡，
  // 請求層級失敗和欄位不符的錯誤訊息混為一談
  expect(res.status).toBe(201);
  expect(res.body.status).toBe('confirmed');
});
```

連 status 都交給 Vitest 判斷，supertest 的請求前置檢查沒派上用場，錯誤定位變模糊。

## ✅ Good

```ts
import { expect } from 'vitest';

it('POST /orders', async () => {
  const res = await request(app.getHttpServer())
    .post('/orders')
    .send(dto)
    .expect(201)                     // supertest：請求層級前置檢查
    .expect('Content-Type', /json/); // supertest

  expect(res.body).toMatchObject({ status: 'confirmed' }); // Vitest：驗 body 細節
});
```

status 與 content-type 用 supertest 鏈式把關，body 結構交給 Vitest matcher。一眼就能分辨失敗是出在請求層級還是資料內容。

## 補充

- supertest 的 `.expect()` 與測試框架無關，換成其他 runner 也成立；只有 `expect()` matcher 是 Vitest 特定的。
- body 該驗到什麼程度見 `assertion-explicit-body`。
