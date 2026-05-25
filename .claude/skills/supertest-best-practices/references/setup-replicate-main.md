---
rule: setup-replicate-main
category: 測試骨架
tags: [setup, nestjs, validation-pipe, global, main]
---

# 在測試中補齊 main.ts 的 global 設定

> `Test.createTestingModule()` 只還原 module 結構，`main.ts` 裡用 `app.useGlobalPipes()` 等手動掛上的 global 設定不會自動套用，必須在測試中補回。

## 原因

- `createNestApplication()` 建出的 app 不會執行 `main.ts`，所以 global pipe、global guard、global interceptor、global filter、global prefix 這些在 `bootstrap()` 裡手動掛的東西都不存在。
- 漏掉 `ValidationPipe` 時，本該回 400 的非法 payload 會被當成合法請求送進 handler，測試於是測到一個 production 根本不會發生的行為。
- 測試環境必須和 production 的請求管線一致，否則 e2e 測試給的綠燈是假的。

## ❌ Bad

```ts
const app = moduleRef.createNestApplication();
await app.init();
// main.ts 裡有 app.useGlobalPipes(new ValidationPipe({ whitelist: true }))，
// 這裡卻沒補上，DTO 驗證在測試中完全沒生效
```

測試的 app 少了 production 會有的 `ValidationPipe`，驗證相關的測試案例全部失真。

## ✅ Good

```ts
const app = moduleRef.createNestApplication();

// 與 main.ts 的 bootstrap() 對齊
app.useGlobalPipes(new ValidationPipe({ whitelist: true, transform: true }));
app.setGlobalPrefix('api');

await app.init();
```

把 `main.ts` 裡所有手動掛的 global 設定原樣搬進測試 setup，請求管線才會和 production 一致。

## 補充

- 用 `APP_PIPE` / `APP_GUARD` 等 module provider 註冊的 global，會隨 module 一起建立，不需要在這裡重掛，只有 `main.ts` 裡手動 `app.useXxx()` 的部分要補。
- 集中補在 factory 裡最不易漏，見 `setup-test-factory`。
