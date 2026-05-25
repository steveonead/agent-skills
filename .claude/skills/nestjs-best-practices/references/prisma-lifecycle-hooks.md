---
rule: prisma-lifecycle-hooks
category: Prisma 整合
tags: [prisma, lifecycle, shutdown]
---

# PrismaService 用生命週期 hook 管連線

> `PrismaService` 在 `onModuleInit` 連線，並依賴 NestJS 的 shutdown hooks 在應用關閉時斷線，不要自己掛 `process.on('beforeExit')`。

## 原因

- 在 `onModuleInit` 明確 `$connect()`，能在啟動階段就確認資料庫連得上，而不是等第一個查詢才連。
- 新版 Prisma 已移除 `beforeExit` 事件，沿用舊的 `process.on('beforeExit')` 寫法不會被觸發。
- 改靠 NestJS 的 `enableShutdownHooks()` 搭配 `OnModuleDestroy` 斷線，與框架生命週期一致。

## ❌ Bad

```ts
@Injectable()
export class PrismaService extends PrismaClient {
  // 新版 Prisma 已移除 beforeExit 事件，這段不會被觸發
  async enableShutdownHooks(app: INestApplication) {
    this.$on('beforeExit', async () => {
      await app.close();
    });
  }
}
```

沿用已移除的 `beforeExit` 事件，關閉邏輯實際上不會執行。

## ✅ Good

```ts
@Injectable()
export class PrismaService
  extends PrismaClient
  implements OnModuleInit, OnModuleDestroy
{
  async onModuleInit() {
    await this.$connect(); // 啟動時就建立連線
  }

  async onModuleDestroy() {
    await this.$disconnect(); // 應用關閉時斷線
  }
}

// main.ts：啟用 shutdown hooks，OnModuleDestroy 才會在收到終止訊號時觸發
app.enableShutdownHooks();
```

連線在 `onModuleInit` 建立、`onModuleDestroy` 釋放，搭配 `enableShutdownHooks()` 與框架生命週期對齊。
