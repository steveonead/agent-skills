---
rule: lifecycle-graceful-shutdown
category: Lifecycle
tags: [lifecycle, shutdown, hooks]
---

# 開啟 graceful shutdown

> 用 `app.enableShutdownHooks()` 啟用關閉鉤子，並在 provider 實作 `OnApplicationShutdown` / `OnModuleDestroy` 收尾連線與資源，讓應用收到終止訊號時乾淨關閉。

## 原因

- 沒啟用 shutdown hooks，收到 `SIGTERM`（如容器重啟）時會直接中斷，進行中的請求被砍、連線沒釋放。
- `enableShutdownHooks()` 會在終止訊號時觸發 `OnModuleDestroy` / `OnApplicationShutdown`，給資源釋放的機會。
- 資料庫連線、訊息佇列、計時器等都該在這些 hook 內正確關閉，避免連線洩漏或資料遺失。

## ❌ Bad

```ts
async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  await app.listen(3000);
  // 沒 enableShutdownHooks，SIGTERM 時直接中斷，連線與資源來不及釋放
}
```

收到終止訊號時硬中斷，進行中的工作與連線都沒有收尾機會。

## ✅ Good

```ts
async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  app.enableShutdownHooks(); // 啟用關閉鉤子
  await app.listen(3000);
}

@Injectable()
export class QueueConsumer implements OnApplicationShutdown {
  async onApplicationShutdown(signal?: string) {
    await this.consumer.stop(); // 停止接新訊息，等手上的處理完
  }
}
```

啟用 shutdown hooks 後，收到 `SIGTERM` 會觸發各 provider 的收尾邏輯，連線與佇列消費者都能優雅關閉。與 `prisma-lifecycle-hooks` 搭配，確保資料庫連線也正確釋放。
