---
rule: v4-strict-loose-object
category: Zod 4 API 強制
tags: [v4, object, strict, loose, deprecated]
---

# 用 `z.strictObject()` / `z.looseObject()`

> Zod 4 提供 top-level 的 `z.strictObject()` 與 `z.looseObject()`，取代 `.strict()` / `.passthrough()` / `.strip()` 等 method。後者全部已 deprecate，但仍維持相容。

## 原因

- top-level 函式表達意圖更直接，閱讀程式碼時不需追到鏈式呼叫的最後
- `.strip()` 本來就是 `z.object()` 的預設行為，存在意義低
- v4 內部已轉用 top-level 形式，未來會更穩定

## ❌ Bad

```ts
import { z } from "zod";

const StrictUser = z.object({
  name: z.string(),
  age: z.number(),
}).strict();

const LooseConfig = z.object({
  port: z.number(),
}).passthrough();

const ExplicitStrip = z.object({
  id: z.string(),
}).strip();
```

## ✅ Good

```ts
import { z } from "zod";

const StrictUser = z.strictObject({
  name: z.string(),
  age: z.number(),
});

const LooseConfig = z.looseObject({
  port: z.number(),
});

const DefaultStripUser = z.object({
  id: z.string(),
});
```

選擇準則：
- 嚴格擋多餘欄位（API request body 防呆） → `z.strictObject()`
- 保留未知欄位（轉發第三方 payload） → `z.looseObject()`
- 移除未知欄位（多數場景） → `z.object()` 預設行為即可

## 例外

從既有大型 schema 衍生時，用 `z.object(schema.shape)` 切換成預設 strip 行為仍是合理寫法。
