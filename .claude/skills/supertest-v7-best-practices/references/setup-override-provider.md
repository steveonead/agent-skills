---
rule: setup-override-provider
category: 測試骨架
tags: [setup, nestjs, overrideProvider, mock]
---

# 用 overrideProvider 替換相依，別改 production module

> 要在 e2e 測試中替換某個 service、repo 或外部 client 時，用 `Test.createTestingModule()` 的 `.overrideProvider().useValue()`，不要去動 production 的 module 定義。

## 原因

- `overrideProvider` 是 NestJS 官方提供的測試替身機制，只在測試的 module context 生效，不污染 production 程式碼。
- 把測試用的 mock 寫進 production module（例如加條件判斷切換實作）會讓 production 帶著測試邏輯上線，是明顯的 code smell。
- override 同時支援 `useValue`、`useClass`、`useFactory`，也有對應的 `overrideGuard`、`overrideInterceptor`、`overrideFilter`，覆蓋面足夠。

## ❌ Bad

```ts
// production 的 module 裡塞測試判斷
@Module({
  providers: [
    {
      provide: PaymentClient,
      useClass: process.env.NODE_ENV === 'test' ? FakePaymentClient : PaymentClient,
    },
  ],
})
export class PaymentModule {}
```

production module 因為測試需求長出環境分支，測試替身的邏輯被帶進正式程式碼，責任邊界變得模糊。

## ✅ Good

```ts
const moduleRef = await Test.createTestingModule({ imports: [AppModule] })
  .overrideProvider(PaymentClient)
  .useValue({ charge: vi.fn().mockResolvedValue({ status: 'paid' }) })
  .compile();

const app = moduleRef.createNestApplication();
await app.init();
```

替換只發生在測試的 module，production module 維持乾淨。需要替換 guard 改用 `.overrideGuard()`，其餘同理。

## 補充

- e2e 的資料層通常直接連測試 DB（靠環境變數切換），不必 override，見 `isolation-test-db`；只有要完全不碰真實 DB 時，才 override `PrismaService` 為假實作。
- 若要保留真實 guard 來測完整 auth flow，就不要 override 它，改在 `beforeAll` 產生真實 token，見 `request-set-auth`。
- override 通常放在 factory 裡，見 `setup-test-factory`。
