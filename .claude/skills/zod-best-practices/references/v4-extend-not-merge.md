---
rule: v4-extend-not-merge
category: Zod 4 API 強制
tags: [v4, object, extend, merge, deprecated]
---

# 用 `.extend()`，不要用 `.merge()`

> `.merge()` 在 Zod 4 已 deprecate。`.extend()` 提供同樣的合併能力，避免 strictness 繼承的歧義，且 TypeScript 編譯效能更好。

## 原因

- `.merge()` 在處理 strict / passthrough 的繼承時行為不明確
- `.extend()` 在 v4 經過重寫，多次連續呼叫也不會觸發 "possibly infinite" TS 錯誤
- 維護兩種合併 API 增加學習成本，v4 統一為 `.extend()`

## ❌ Bad

```ts
import { z } from "zod";

const Base = z.object({ id: z.uuid() });
const Timestamps = z.object({
  createdAt: z.iso.datetime(),
  updatedAt: z.iso.datetime(),
});

const Entity = Base.merge(Timestamps);
```

## ✅ Good

```ts
import { z } from "zod";

const Base = z.object({ id: z.uuid() });

const Entity = Base.extend({
  createdAt: z.iso.datetime(),
  updatedAt: z.iso.datetime(),
});

const FullEntity = Entity.extend({
  name: z.string().min(1),
}).extend({
  archived: z.boolean(),
});
```

`.extend()` 也可以覆寫既有欄位，做法直觀：

```ts
const AdminUser = User.extend({
  role: z.literal("admin"),
});
```

## 例外

需要把整個 schema 視為「子集合併」而非「逐欄位 extend」時，可考慮 `z.intersection()`，但多數情境 `.extend()` 已足夠。
