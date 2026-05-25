---
rule: setup-get-http-server
category: 測試骨架
tags: [setup, nestjs, getHttpServer]
---

# 用 app.getHttpServer() 取得底層 server

> 對 NestJS app 一律傳 `request(app.getHttpServer())`，讓 supertest 拿到 Nest 底層的 HTTP listener。

## 原因

- `app.getHttpServer()` 回傳的是 Nest 包好的底層 HTTP server，supertest 會把它綁到 ephemeral port 再送請求，請求會完整經過 Nest 的 guard、pipe、interceptor、filter。
- 直接把 `INestApplication` 或 Express instance 傳給 `request()` 都不對，前者不是 supertest 認得的 server，後者繞過了 Nest 的請求生命週期。
- 這是 NestJS 官方文件的標準寫法，團隊之間一致性高，後人接手不需要猜。

## ❌ Bad

```ts
// 直接把 INestApplication 傳進去
await request(app).get('/cats').expect(200);
// app 不是 http.Server，supertest 無法正確處理
```

把 `app` 當成 server 傳入，supertest 拿不到可監聽的 server，請求不會正確送出。

## ✅ Good

```ts
import request from 'supertest';

it('GET /cats', async () => {
  await request(app.getHttpServer())
    .get('/cats')
    .expect(200);
});
```

固定用 `app.getHttpServer()` 取得底層 server，請求會走完整條 Nest 管線，測到的行為才貼近真實流量。

## 補充

- 若把 server 重複用在多個請求，可在 factory 內先存成變數，見 `setup-test-factory`。
- server 由 supertest 綁 ephemeral port 的細節見 `cleanup-ephemeral-port`。
