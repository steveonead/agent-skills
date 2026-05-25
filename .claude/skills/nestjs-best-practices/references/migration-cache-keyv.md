---
rule: migration-cache-keyv
category: v10 → v11 遷移
tags: [migration, cache, keyv]
---

# CacheModule 改用 Keyv

> NestJS 11 的 `@nestjs/cache-manager` 升級到新版 `cache-manager`，底層改用 Keyv，store 設定方式與快取資料格式都有變動。

## 原因

- v11 的 `CacheModule` 透過 Keyv 提供跨 backend 的統一 key-value 介面，舊的 store 設定寫法需要調整。
- 升級後快取資料的儲存格式改變，舊版寫入的資料無法直接相容，需要清快取或重新暖機。
- Redis 等外部 store 改透過 Keyv adapter 接入，不再直接傳舊版 store factory。

## ❌ Bad

```ts
// v10 寫法：直接傳舊版 redis store
CacheModule.register({
  store: redisStore,
  host: 'localhost',
  port: 6379,
});
```

舊的 store 寫法在 v11 不再適用，且未考量資料格式相容問題。

## ✅ Good

```ts
import { CacheModule } from '@nestjs/cache-manager';
import { createKeyv } from '@keyv/redis';

CacheModule.registerAsync({
  isGlobal: true,
  useFactory: () => ({
    stores: [createKeyv('redis://localhost:6379')],
  }),
});
```

改用 Keyv adapter 設定 store。升級時記得快取資料格式已變，部署後舊資料視為 miss，須評估暖機策略。

## 例外

沒有使用 `@nestjs/cache-manager` 的專案不適用此規則。
