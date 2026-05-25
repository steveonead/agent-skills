---
name: supertest-v7-best-practices
description: SuperTest v7 最佳實踐規則集，供撰寫、審查或重構 HTTP e2e 測試時參考。明確以 NestJS + Vitest 為測試環境，涵蓋 v7 / superagent v9~v10 的 breaking change 與社群、官方推薦寫法。適用於新增 e2e 測試、PR self-review、supertest v6 → v7 migration。不適用於 GraphQL e2e、Fastify adapter 差異，或 Vitest / NestJS testing module 自身的使用慣例。
---

# SuperTest v7 Best Practices

這份規則集聚焦 SuperTest v7 在 NestJS 應用上的 e2e 測試。SuperTest 是獨立的 HTTP 測試庫，本身不綁定任何 test runner，因此規則分成兩層：一層是與框架無關的 supertest 本身用法，一層是與 Vitest 整合的接點。掌握這兩層界線，才能寫出穩定、不卡住、行為對齊 production 的 e2e 測試。

## 適用時機

參考這份規則集的時機：
- 撰寫新的 NestJS e2e 測試
- 審查現有 e2e 測試的品質
- 從 supertest v6 升級到 v7，或排查升級後的相容問題

## 規則分類

| 分類 | 前綴 |
|------|------|
| 版本與遷移 | `migration-` |
| 測試骨架 | `setup-` |
| 請求撰寫 | `request-` |
| 斷言 | `assertion-` |
| 清理與生命週期 | `cleanup-` |
| 測試隔離 | `isolation-` |

## 規則速查

### 版本與遷移

- `migration-superagent-bump` — v7 底層改用 superagent v9 / v10，連帶繼承其 breaking change
- `migration-pin-safe-version` — 釘 supertest `>= 7.1.3` 搭 superagent `>= 10.2.2`，避開中間版本的 server lifecycle bug
- `migration-http2-option` — 需測 HTTP/2 時用 `request(app, { http2: true })` 初始化

### 測試骨架

- `setup-import-syntax` — 依 `esModuleInterop` 決定 import 寫法，別用 `import { request }`
- `setup-get-http-server` — 一律用 `request(app.getHttpServer())` 取得 Nest 底層 server
- `setup-lifecycle-hooks` — `beforeAll` 建 module 並 `app.init()`，`afterAll` 收尾
- `setup-test-factory` — 用 factory function 封裝 testing module 建立，回傳測試所需物件
- `setup-replicate-main` — 在測試中手動補上 `main.ts` 的 global pipes / guards / prefix
- `setup-override-provider` — 用 `overrideProvider().useValue()` 替換相依，而非改 production module

### 請求撰寫

- `request-await-or-return` — 每個 request chain 必須 `await` 或 `return`
- `request-agent-session` — 需維持登入狀態時用 `request.agent(server)` 自動帶 cookie
- `request-set-auth` — 用 `.set('Authorization', ...)` 帶 token，避免每次重打登入
- `request-file-upload` — 檔案上傳用 `.field()` + `.attach()`，留意 superagent v10 的 formidable v3 差異

### 斷言

- `assertion-supertest-vs-vitest` — 釐清 supertest `.expect()` 與 Vitest `expect()` 兩個來源的分工
- `assertion-explicit-body` — 不要只斷言 status code，明確驗證 response body 結構

### 清理與生命週期

- `cleanup-close-app` — `afterAll` 一定 `await app.close()`，否則 process 卡住不退出
- `cleanup-ephemeral-port` — 讓 supertest 綁 ephemeral port，別手動 `listen` 固定 port
- `cleanup-hanging-process` — 卡住時用 Vitest 的 `hanging-process` reporter 追查未清的 handle

### 測試隔離

- `isolation-test-db` — 用獨立或 in-memory DB，並在 hook 清資料，避免測試互相污染

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
