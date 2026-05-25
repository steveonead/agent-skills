---
rule: config-validate-on-startup
category: 設定管理
tags: [config, zod, validation, env]
---

# 啟動時用 Zod schema 驗證環境變數

> `ConfigModule.forRoot` 的 `validate` 用 Zod schema 驗證環境變數，缺漏或格式錯誤就讓應用在啟動時直接失敗（fail fast）。

## 原因

- 環境變數沒驗證的話，缺漏要到第一次用到時才報錯，可能是部署後跑很久才出錯，難以追查。
- 啟動時一次驗證所有設定，錯誤即時暴露，不會帶著半殘的設定上線。
- 用 Zod 驗證可順便把字串轉成正確型別（如 `PORT` 轉 number），下游拿到的就是 typed 值。

> 此處只談如何把 schema 接進 `ConfigModule`，不涉及 schema 本身的寫法。

## ❌ Bad

```ts
ConfigModule.forRoot({ isGlobal: true });

// 用的時候才發現沒設，且型別是 string | undefined
const port = process.env.PORT; // string | undefined
```

沒驗證，缺漏拖到 runtime 才報錯，型別也不可靠。

## ✅ Good

```ts
import { z } from 'zod';

const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'test', 'production']),
  PORT: z.coerce.number().default(3000),
  DATABASE_URL: z.url(),
});

ConfigModule.forRoot({
  isGlobal: true,
  validate: (config) => envSchema.parse(config), // 啟動時驗證，失敗即 throw
});
```

啟動時用 Zod 驗證並轉型，缺 `DATABASE_URL` 或格式錯誤就立刻啟動失敗，下游拿到的 `PORT` 已是 number。
