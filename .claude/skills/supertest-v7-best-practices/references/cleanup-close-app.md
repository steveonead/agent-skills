---
rule: cleanup-close-app
category: 清理與生命週期
tags: [cleanup, afterAll, app-close, open-handle]
---

# afterAll 一定要 await app.close()

> 每個建了 app 的 describe，`afterAll` 都要 `await app.close()`，否則底層 server 與連線不會釋放，process 跑完測試後卡住不退出。

## 原因

- `app.init()` 啟動的 server、DB 連線、background timer 都掛在 event loop 上，沒關閉的話 Vitest 的 worker process 無法正常結束。
- 不關 app 的症狀是測試明明全綠，process 卻遲遲不退、CI 因此 timeout，或被迫用 `--no-file-parallelism` 之類的權宜手段掩蓋。
- `app.close()` 是 Promise，必須 `await`，否則 `afterAll` 在關閉完成前就結束，等於沒關。

## ❌ Bad

```ts
describe('Cats (e2e)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleRef = await Test.createTestingModule({ imports: [AppModule] }).compile();
    app = moduleRef.createNestApplication();
    await app.init();
  });

  // 沒有 afterAll，或有 afterAll 卻忘了 await
  // afterAll(() => { app.close(); }); // 沒 await，關閉沒完成就結束
});
```

app 開了沒關，server 與連線一直掛著，測試跑完 process 卡住，CI 只能等到 timeout。

## ✅ Good

```ts
describe('Cats (e2e)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleRef = await Test.createTestingModule({ imports: [AppModule] }).compile();
    app = moduleRef.createNestApplication();
    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });
});
```

`afterAll` 確實 `await app.close()`，server 與相依連線一併釋放，process 測完就乾淨退出。

## 補充

- `app.close()` 會連帶觸發 Nest 的 lifecycle hook（如 `OnModuleDestroy`）。Prisma 連線要在 `PrismaService` 實作 `async onModuleDestroy() { await this.$disconnect(); }`，才會隨 `app.close()` 一併關閉；若另開獨立連線仍要自行收尾。
- process 還是卡住時，用 `cleanup-hanging-process` 追出沒被釋放的 handle。
