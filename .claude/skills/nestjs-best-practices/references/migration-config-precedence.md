---
rule: migration-config-precedence
category: v10 → v11 遷移
tags: [migration, config, env]
---

# ConfigModule 讀取順序與 validatePredefined

> 升級到 `@nestjs/config@4` 後，環境變數讀取順序改變，`ignoreEnvVars` 已被 `validatePredefined` 取代。

## 原因

- v11 搭配的 `@nestjs/config@4` 調整了 `ConfigService#get` 讀值的優先序，沿用 v3 的假設可能拿到非預期的值。
- 舊的 `ignoreEnvVars` 選項已 deprecate，繼續使用會失效且行為不明確。
- 啟動前就存在的 predefined 變數（如 `PORT=3000 node main.js`）與從 `.env` 載入的變數，驗證行為不同，需要分清楚。

## ❌ Bad

```ts
ConfigModule.forRoot({
  isGlobal: true,
  // ignoreEnvVars 在 v4 已 deprecate，無法再用來跳過 process.env 驗證
  ignoreEnvVars: true,
  validationSchema: someSchema,
});
```

沿用 `ignoreEnvVars` 不會有預期效果，而且沒意識到讀取順序已改變，可能誤判 `.env` 會蓋過 runtime 變數。

## ✅ Good

```ts
ConfigModule.forRoot({
  isGlobal: true,
  // 不驗證啟動前就設好的 process.env 變數時，用 validatePredefined: false
  validatePredefined: false,
  validate: (config) => envSchema.parse(config),
});
```

明確改用 `validatePredefined`，並理解 v4 真正的 breaking change：`ConfigService#get` 的讀取優先序改為 internal configuration → validated 環境變數 → `process.env`，也就是程式內以 `registerAs` 定義的設定現在會蓋過同名環境變數。升級時逐一檢查依賴讀值順序的設定。

## 例外

僅維護中、尚未升級到 `@nestjs/config@4` 的專案不適用此規則。
