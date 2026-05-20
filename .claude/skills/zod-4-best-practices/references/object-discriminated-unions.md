---
rule: object-discriminated-unions
category: 物件 Schema
tags: [object, union, discriminated, type-narrowing]
---

# 標籤式 union 用 `z.discriminatedUnion()`

> 多個物件 schema 透過某個共同欄位區分（例如 `type: "image" | "video"`）時，用 `z.discriminatedUnion()` 而非 `z.union()`。後者每個分支都要試 parse 一次，且 TypeScript narrow 不出來。

## 原因

- `z.union()` 對每個分支試 parse，所有錯誤都收集起來，效能差且錯誤訊息混亂
- `z.discriminatedUnion()` 看 discriminator 直接挑分支，效能與訊息都好
- TypeScript 對 discriminated union 能自動 narrow，呼叫端用起來舒服
- Zod 4 升級後 discriminator 還支援 union / pipe（不只是單一 literal）

## ❌ Bad

```ts
import { z } from "zod";

const Media = z.union([
  z.object({
    type: z.literal("image"),
    url: z.url(),
    width: z.number(),
  }),
  z.object({
    type: z.literal("video"),
    url: z.url(),
    duration: z.number(),
  }),
]);

const m = Media.parse(input);
if (m.type === "image") m.width;
```

驗證失敗時錯誤訊息會把所有分支的不符都列出來，使用者一頭霧水。

## ✅ Good

```ts
import { z } from "zod";

const Media = z.discriminatedUnion("type", [
  z.object({
    type: z.literal("image"),
    url: z.url(),
    width: z.number(),
  }),
  z.object({
    type: z.literal("video"),
    url: z.url(),
    duration: z.number(),
  }),
]);

const m = Media.parse(input);
if (m.type === "image") m.width.toFixed(0);
```

Zod 4 新增的 union / pipe discriminator：

```ts
const Status = z.discriminatedUnion("status", [
  z.object({ status: z.literal("ok"), data: z.unknown() }),
  z.object({ status: z.union([z.literal("error"), z.literal("fail")]) }),
]);
```

## 例外

各分支沒有共同 discriminator 欄位（純結構區分）時才用 `z.union()`。多數場景應該重新設計，加入 discriminator 欄位。
