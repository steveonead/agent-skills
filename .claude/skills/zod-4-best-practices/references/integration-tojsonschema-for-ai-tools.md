---
rule: integration-tojsonschema-for-ai-tools
category: 整合能力
tags: [integration, json-schema, ai, openapi, v4]
---

# AI tool input / OpenAPI 用 `z.toJSONSchema()`

> Zod 4 內建 `z.toJSONSchema()`，可直接把 schema 轉成 JSON Schema。用在 LLM tool input、OpenAPI 文件、structured output，避免手寫 JSON Schema 與 Zod schema 兩份。

## 原因

- 手寫 JSON Schema 與 Zod 一定會 drift，特別是欄位增刪時
- LLM tool definition、Anthropic / OpenAI structured output 都吃 JSON Schema
- `z.toJSONSchema()` 是 v4 first-party，過去依賴的 `zod-to-json-schema` 等第三方套件可改用內建取代

## ❌ Bad

```ts
import { z } from "zod";

const SearchInput = z.object({
  query: z.string(),
  limit: z.number().int().min(1).max(50).default(10),
});

const tool = {
  name: "search",
  input_schema: {
    type: "object",
    properties: {
      query: { type: "string" },
      limit: { type: "integer", minimum: 1, maximum: 50, default: 10 },
    },
    required: ["query"],
  },
};
```

修改 Zod schema 後，需手動同步更新 JSON Schema。

## ✅ Good

```ts
import { z } from "zod";

const SearchInput = z.object({
  query: z.string().describe("搜尋關鍵字"),
  limit: z.number().int().min(1).max(50).default(10),
});

const tool = {
  name: "search",
  input_schema: z.toJSONSchema(SearchInput),
};

const openApiSchema = z.toJSONSchema(SearchInput, {
  target: "openapi-3.0",
});
```

常用選項：
- `target: "draft-2020-12" | "draft-07" | "openapi-3.0"` — 對應消費端版本
- `unrepresentable: "throw" | "any"` — 處理無法表達的型別（如 `bigint`）
- `cycles: "ref" | "throw"` — 處理 cyclic schema

## 例外

JSON Schema 需求極特殊（例如非標準 vendor extension）時，仍可能要手寫；這時把 `z.toJSONSchema()` 的結果當 base，再客製後處理。
