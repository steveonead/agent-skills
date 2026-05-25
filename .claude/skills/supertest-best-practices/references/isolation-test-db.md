---
rule: isolation-test-db
category: 測試隔離
tags: [isolation, database, cleanup, in-memory]
---

# 用獨立 / in-memory DB 並逐測試清資料

> e2e 測試要連獨立的測試資料庫或 in-memory 實例，絕不碰開發或 production DB，並在 hook 清資料避免測試互相污染。

## 原因

- e2e 測試會實際寫入資料，直接打開發或 production DB 等於拿真實資料當測試場，污染甚至破壞既有資料。
- 測試之間若共用資料且不清理，前一個 test 留下的狀態會讓後一個 test 的結果隨執行順序變動，產生難查的 flaky。
- 用獨立測試 DB（或 in-memory / 容器化實例）加上每個 test 後清資料，每個案例都從乾淨狀態出發，結果穩定可重現。

## ❌ Bad

```ts
// 測試直接連開發用的 DB，且跑完不清資料
beforeAll(async () => {
  const moduleRef = await Test.createTestingModule({
    imports: [AppModule], // AppModule 連的是 .env 裡的開發 DB
  }).compile();
  app = moduleRef.createNestApplication();
  await app.init();
});
// 沒有任何資料清理，測試殘留的訂單一筆筆累積在開發 DB
```

測試寫進開發 DB 又不清理，既污染真實資料，殘留狀態還讓後續測試結果隨執行順序變動。

## ✅ Good

```ts
let app: INestApplication;
let prisma: PrismaService;

beforeAll(async () => {
  // DATABASE_URL 已在測試啟動前指向獨立測試 DB（見補充）。
  // PrismaService 的 constructor 讀這個環境變數，所以不需要 override。
  const moduleRef = await Test.createTestingModule({ imports: [AppModule] }).compile();
  app = moduleRef.createNestApplication();
  await app.init();
  prisma = moduleRef.get(PrismaService);
});

afterEach(async () => {
  await prisma.order.deleteMany(); // 每個 test 後清資料，回到乾淨狀態
});

afterAll(async () => {
  await app.close();
});
```

靠環境變數讓 `PrismaService` 連到獨立測試 DB，並在 `afterEach` 用 `deleteMany()` 清資料，每個 test 都從一致的起點開始，結果穩定。

## 補充

- `PrismaService` 的 constructor 若直接讀 `process.env.DATABASE_URL`（用 `datasourceUrl` 傳入），就用 Vitest 的 `setupFiles` 或載入 `.env.test` 在測試啟動前把它指向測試 DB，`PrismaService` 即連對，毋須 override。
- Prisma 清資料用 `deleteMany()`，注意外鍵順序（先刪子表再刪父表），或在交易裡用 `$transaction` 批次清。
- 測試 DB 可用獨立 schema 或容器化實例（如 testcontainers）。Prisma 搭 SQLite 雖快，但與 production 的 PostgreSQL / MySQL 行為可能有差異，關鍵流程仍建議用同型別的 DB。
- 測試 DB 連線若沒隨 `app.close()` 一起關，會造成 process 卡住，見 `cleanup-close-app` 與 `cleanup-hanging-process`。
- 相依替換的機制見 `setup-override-provider`。
