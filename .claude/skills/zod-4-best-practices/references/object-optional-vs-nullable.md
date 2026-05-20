---
rule: object-optional-vs-nullable
category: 物件 Schema
tags: [object, optional, nullable, semantics]
---

# `.optional()` 與 `.nullable()` 語意要分清楚

> `.optional()` 表示「欄位可以省略」（值為 `undefined` 或不存在），`.nullable()` 表示「值可以是 `null`」。兩者語意不同，混用會傳染整個 API。

## 原因

- HTTP / JSON 場景 `undefined`（key 不存在）與 `null`（key 存在但值為 null）會走不同分支
- 資料庫 nullable column 應該對應 `.nullable()`，不該用 `.optional()` 假裝
- 同時允許省略與 null 才用 `.nullish()`，意圖明確才寫

## ❌ Bad

```ts
import { z } from "zod";

const User = z.object({
  middleName: z.string().optional(),
  deletedAt: z.iso.datetime().optional(),
});

const dbRow = { middleName: null, deletedAt: null };
User.parse(dbRow);
```

DB 給回來 `null`，但 schema 寫 `.optional()`（預期 `undefined`），parse 失敗。

## ✅ Good

```ts
import { z } from "zod";

const User = z.object({
  middleName: z.string().nullable(),
  deletedAt: z.iso.datetime().nullable(),

  nickname: z.string().optional(),

  bio: z.string().nullish(),
});
```

判斷準則：
- 對應資料庫 nullable column / API 回 `null` → `.nullable()`
- HTTP request 可以「不傳」、預設值場景 → `.optional()`
- 兩者都接受（極少數）→ `.nullish()`

## 例外

對外 API 為求相容性接受 `null` 與省略視為同義時，可以用 `.nullish()`，但 schema 註解要寫清楚這是刻意設計。
