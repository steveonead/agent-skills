---
rule: setup-test-factory
category: 測試骨架
tags: [setup, factory, harness, nestjs]
---

# 用 factory function 封裝 app 建立

> 把 testing module 的建立抽成一個 factory function，回傳測試需要的 app 與 service / repo，取代散落在 describe 裡的一堆 `let` 與 `moduleRef.get()`。

## 原因

- e2e 測試的 setup 通常包含建 module、套 global config、取出要驗證的 service 與 repo，直接攤在 `beforeAll` 裡會讓每個測試檔重抄一遍。
- factory 把這些細節收斂成一個入口，測試檔只 destructure 需要的東西，意圖清楚、也好維護。
- 多個測試檔共用同一套 setup 時，factory 是唯一的真實來源，改一處就同步。

## ❌ Bad

```ts
describe('Orders (e2e)', () => {
  let app: INestApplication;
  let ordersService: OrdersService;
  let prisma: PrismaService;

  beforeAll(async () => {
    const moduleRef = await Test.createTestingModule({ imports: [AppModule] }).compile();
    app = moduleRef.createNestApplication();
    app.useGlobalPipes(new ValidationPipe());
    await app.init();
    ordersService = moduleRef.get(OrdersService);
    prisma = moduleRef.get(PrismaService);
    // 每個測試檔都複製這一整段，改 global config 要逐檔同步
  });
});
```

setup 細節散在 `beforeAll`，每個測試檔各抄一份，global config 一改就得全檔追著改。

## ✅ Good

```ts
// test/helpers/create-orders-app.ts
type OrdersTestApp = {
  app: INestApplication;
  ordersService: OrdersService;
  prisma: PrismaService;
};

// 標註回傳型別，讓 factory 對測試檔形成明確契約
export async function createOrdersTestApp(): Promise<OrdersTestApp> {
  const moduleRef = await Test.createTestingModule({ imports: [AppModule] }).compile();

  const app = moduleRef.createNestApplication();
  app.useGlobalPipes(new ValidationPipe()); // 對齊 main.ts
  await app.init();

  return {
    app,
    ordersService: moduleRef.get(OrdersService),
    prisma: moduleRef.get(PrismaService),
  };
}
```

```ts
// orders.e2e-spec.ts
describe('Orders (e2e)', () => {
  let app: INestApplication;
  let ordersService: OrdersService;

  beforeAll(async () => {
    ({ app, ordersService } = await createOrdersTestApp());
  });

  afterAll(async () => {
    await app.close();
  });
});
```

factory 收斂所有建立細節，測試檔只取需要的物件。global config 集中在一處，跨檔一致。

## 補充

- 這條是純結構約定，重點在「把 setup 收進 factory」，不規範 factory 內部要回傳哪些東西。
- factory 內要對齊 main.ts 的 global config，見 `setup-replicate-main`。
- 相依替換可在 factory 裡做，見 `setup-override-provider`。
