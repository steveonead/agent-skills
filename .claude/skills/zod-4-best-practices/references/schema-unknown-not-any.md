---
rule: schema-unknown-not-any
category: Schema 定義
tags: [schema, type-safety, any, unknown]
---

# 用 `z.unknown()` 取代 `z.any()`

> Zod schema 內出現 `z.any()` 等於繞過 TypeScript 與 Zod 雙重型別保護，直接讓垃圾資料流進系統。一律用 `z.unknown()`。

## 原因

- `z.any()` 推出來的型別是 `any`，會關掉所有後續欄位的型別檢查
- `z.unknown()` 推出來的型別是 `unknown`，使用前必須先 narrow，強迫呼叫端負責
- Schema 用 `any` 表示「不在乎驗證」，那為什麼還要寫 schema

## ❌ Bad

```ts
import { z } from "zod";

const WebhookPayload = z.object({
  event: z.string(),
  data: z.any(),
});

function handle(payload: z.infer<typeof WebhookPayload>) {
  payload.data.userId.toUpperCase();
}
```

`payload.data` 被推成 `any`，整條鏈一路關閉型別檢查，runtime 才會 throw。

## ✅ Good

```ts
import { z } from "zod";

const WebhookPayload = z.object({
  event: z.string(),
  data: z.unknown(),
});

function handle(payload: z.infer<typeof WebhookPayload>) {
  const data = z.object({ userId: z.string() }).parse(payload.data);
  data.userId.toUpperCase();
}
```

`unknown` 強迫呼叫端再做一次 narrow（用另一個 schema 或 type guard），保留型別安全。

## 例外

只有當資料 **真的** 沒有可預期結構（例如 logger 透明轉發任意 JSON）才考慮 `z.any()`，但這種場景幾乎都可以用 `z.unknown()` + `z.json()` 表達。
