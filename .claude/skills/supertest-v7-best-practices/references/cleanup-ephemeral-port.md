---
rule: cleanup-ephemeral-port
category: 清理與生命週期
tags: [cleanup, port, ephemeral, parallel, race]
---

# 讓 supertest 綁 ephemeral port，別手動 listen 固定 port

> 把 `app.getHttpServer()` 交給 supertest，它會自動綁一個臨時 port，不要自己 `app.listen(3000)` 固定 port，否則平行測試會 port 衝突。

## 原因

- supertest 收到還沒 listen 的 server 時，會幫你綁一個 ephemeral port、跑完請求再放掉，完全不需要管 port。
- 自己 `listen(3000)` 固定 port 後，Vitest 平行跑多個測試檔時會有多個 process 搶同一個 port，直接 `EADDRINUSE`。
- 固定 port 也常見忘了關 server，是 process 卡住的另一個來源。

## ❌ Bad

```ts
beforeAll(async () => {
  const moduleRef = await Test.createTestingModule({ imports: [AppModule] }).compile();
  app = moduleRef.createNestApplication();
  await app.init();
  await app.listen(3000); // 固定 port，平行測試互搶，EADDRINUSE
  server = app.getHttpServer();
});
```

手動綁固定 port，多個測試檔平行跑時搶同一個 port，CI 上偶發 `EADDRINUSE` 直接失敗。

## ✅ Good

```ts
beforeAll(async () => {
  const moduleRef = await Test.createTestingModule({ imports: [AppModule] }).compile();
  app = moduleRef.createNestApplication();
  await app.init(); // 不 listen，supertest 會自己綁 ephemeral port
});

it('GET /cats', async () => {
  await request(app.getHttpServer()).get('/cats').expect(200);
});
```

只 `app.init()` 不 `listen`，把 server 交給 supertest 綁臨時 port，平行測試各用各的 port，互不干擾。

## 補充

- e2e 測試幾乎不需要 `app.listen()`，那是 production bootstrap 才做的事。
- 真要對固定 port 發請求（如測 WebSocket）時，記得在 `afterAll` 關閉，見 `cleanup-close-app`。
- v7.1.0 修過 server re-use 的 race condition，搭配版本見 `migration-pin-safe-version`。
