---
name: nestjs-best-practices
description: NestJS 最佳實踐規則集。撰寫、審查或重構 controller、service、module 時使用，涵蓋分層架構、依賴注入、enhancer 管線與 Prisma 整合，搭配 nestjs-zod 驗證、Vitest + SuperTest 測試。不適用於 GraphQL、Microservices。
---

# NestJS 11 Best Practices

這份規則集聚焦 NestJS 11 應用本身的設計與實作，涵蓋 v10 → v11 的 breaking change、模組與分層架構、依賴注入、驗證、錯誤處理、設定、Prisma 整合、測試，以及 Guard / Interceptor / Logging / Lifecycle 等請求管線與維運面向。NestJS 提供 Pipe、Filter、Guard、Interceptor 四種 enhancer，本規則集確保四者都被正確使用，而不是把邏輯全塞進 controller 或 service。

## 適用時機

參考這份規則集的時機：

- 撰寫新的 NestJS 11 controller、service、module 或 provider
- 審查現有 NestJS 程式碼是否符合架構與 v11 慣例
- 從 NestJS 10 升級到 11 的 migration 流程
- AI agent 自動產生 NestJS 程式碼時對齊 v11 與本專案 stack

## 規則分類

| 分類 | 前綴 |
|------|------|
| v10 → v11 遷移 | `migration-` |
| 模組與分層架構 | `architecture-` |
| 依賴注入 | `di-` |
| 驗證（Zod 整合） | `validation-` |
| 錯誤處理 | `error-` |
| 設定管理 | `config-` |
| Prisma 整合 | `prisma-` |
| 測試 | `testing-` |
| Guard | `guard-` |
| Interceptor | `interceptor-` |
| Logging | `logging-` |
| Lifecycle | `lifecycle-` |

## 規則速查

### v10 → v11 遷移

- `migration-config-precedence` — `@nestjs/config@4` 變數讀取順序改變，`ignoreEnvVars` 改用 `validatePredefined`
- `migration-dynamic-module-ref` — 動態模組改以 object reference 判斷相等，共用須先指派成變數再 import
- `migration-cache-keyv` — `CacheModule` 改用 Keyv 統一介面，store 設定需調整

### 模組與分層架構

- `architecture-feature-module-by-domain` — 依業務領域切 feature module，不要在 root 放 `controllers/`、`services/` 這種技術分層資料夾
- `architecture-thin-controller` — controller 只收 request、回傳 response，business logic 一律放 service；破壞性 API 變更用 `app.enableVersioning()` 管理
- `architecture-module-encapsulation` — 模組只 export 對外需要的 provider 當公開 API，內部 repository／細節不外露
- `architecture-avoid-global-module` — 少用 `@Global()`，優先用 `imports` 明確宣告依賴
- `architecture-circular-dependency` — 用事件（`@nestjs/event-emitter`）或抽共用模組解循環依賴，`forwardRef()` 是最後手段
- `architecture-layering` — 維持 controller → service → repository 分層，每個 service 單一職責，repository 用 `select`/`include` 塑形查詢避免 N+1

### 依賴注入

- `di-constructor-injection` — 預設用 constructor injection，不要手動 `new`，也不要把 `ModuleRef` 當 service locator 隱藏依賴
- `di-inject-by-token` — 對外部邊界用 interface + custom token 注入，方便替換與測試
- `di-provider-scope` — 慎用 request-scoped / transient provider，注意效能與依賴傳染

### 驗證（Zod 整合）

- `validation-zod-dto` — 用 `createZodDto(schema)` 從 Zod schema 建 DTO class，取代 class-validator DTO
- `validation-global-zod-pipe` — 全域註冊 `ZodValidationPipe`（`APP_PIPE`），讓 `@Body/@Query/@Param` 自動以 Zod 驗證
- `validation-strict-schema` — 用 `createZodValidationPipe({ strictSchemaDeclaration: true })`，確保每個參數都綁到 Zod DTO 才放行
- `validation-zod-serializer` — 回應用 `ZodSerializerInterceptor` + `@ZodSerializerDto`，按 schema 序列化避免外洩欄位

### 錯誤處理

- `error-builtin-http-exception` — 用內建 `HttpException` 子類別表達錯誤，別自己拼 status code
- `error-global-exception-filter` — 用全域 exception filter 統一錯誤回應格式，並接住 `nestjs-zod` 的 `ZodValidationException`
- `error-prisma-translation` — 在 service/repository 邊界把 Prisma known error（P2002 等）轉成對應 HttpException

### 設定管理

- `config-validate-on-startup` — `ConfigModule.forRoot` 的 `validate` 用 Zod schema，啟動時 fail fast
- `config-typed-access` — 用 `registerAs` + `ConfigService<T>` 取 typed config，不直接讀 `process.env`

### Prisma 整合

- `prisma-injectable-service` — 把 `PrismaClient` 包成 `@Injectable` 的 `PrismaService` 單例注入，別在各 service `new`
- `prisma-lifecycle-hooks` — `PrismaService` 用 `OnModuleInit` 連線，搭配 NestJS shutdown hooks 正確關閉
- `prisma-transaction` — 多步驟寫入用 `$transaction` 確保原子性與一致性

### 測試

- `testing-vitest-swc-decorators` — Vitest 跑 NestJS 需 `unplugin-swc` + `reflect-metadata` 處理 `emitDecoratorMetadata`
- `testing-unit-testing-module` — 單元測 provider 用 `Test.createTestingModule` 組最小 module、用 `overrideProvider` mock 掉相依

### Guard

- `guard-authz` — 認證／授權用 Guard，別在 controller/service 內手刻權限判斷；rate limiting 用 `ThrottlerGuard`

### Interceptor

- `interceptor-cross-cutting` — logging、response 包裝、timeout、cache 等橫切關注用 Interceptor，別散落在 handler

### Logging

- `logging-structured` — 用 Nest `Logger` 或 `nestjs-pino` 做結構化 logging，禁用裸 `console.log`

### Lifecycle

- `lifecycle-graceful-shutdown` — 開 `app.enableShutdownHooks()`，用 `OnApplicationShutdown` / `OnModuleDestroy` 正確收尾連線與資源

## 使用方式

讀取個別規則檔案以取得詳細說明與範例：

```
references/[類別前綴]-[規則名稱].md
```

每個規則檔案包含：
- 說明此規則重要的原因
- 不建議的寫法（含說明）
- 建議的寫法（含說明）
- 補充說明與參考

## 參考來源

- [NestJS 官方文件](https://docs.nestjs.com/)
- [NestJS v11 Migration Guide](https://docs.nestjs.com/migration-guide)
- [Announcing NestJS 11](https://trilon.io/blog/announcing-nestjs-11-whats-new)
- [nestjs-zod](https://github.com/BenLorantfy/nestjs-zod)
- [NestJS Prisma Recipe](https://docs.nestjs.com/recipes/prisma)
