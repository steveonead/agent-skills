---
rule: object-partial-pick-omit
category: 物件 Schema
tags: [object, partial, pick, omit, dry]
---

# 衍生 schema 用 `.partial()` / `.pick()` / `.omit()`

> 為 update、view、create 重新定義 schema 是常見的重複。一律從 base schema 衍生，確保欄位增刪自動同步。

## 原因

- 重新定義等於放棄「schema 是單一真相」這個保證
- 三個 schema 各自演化會出現「create 有的欄位 update 沒有」這類難以追溯的 bug
- `.partial()` / `.pick()` / `.omit()` 是 Zod 4 中保留型別的衍生方式

## ❌ Bad

```ts
import { z } from "zod";

const UserSchema = z.object({
  id: z.uuid(),
  email: z.email(),
  name: z.string().min(1),
  passwordHash: z.string(),
  createdAt: z.iso.datetime(),
});

const CreateUser = z.object({
  email: z.email(),
  name: z.string().min(1),
  password: z.string().min(8),
});

const UpdateUser = z.object({
  email: z.email().optional(),
  name: z.string().min(1).optional(),
});

const PublicUser = z.object({
  id: z.uuid(),
  email: z.email(),
  name: z.string().min(1),
  createdAt: z.iso.datetime(),
});
```

新增欄位須手動逐一同步，極易遺漏。

## ✅ Good

```ts
import { z } from "zod";

const UserSchema = z.object({
  id: z.uuid(),
  email: z.email(),
  name: z.string().min(1),
  passwordHash: z.string(),
  createdAt: z.iso.datetime(),
});

const CreateUser = UserSchema
  .omit({ id: true, passwordHash: true, createdAt: true })
  .extend({ password: z.string().min(8) });

const UpdateUser = CreateUser.partial();

const PublicUser = UserSchema.omit({ passwordHash: true });
```

慣用組合：
- `.pick({...})` — 只保留某些欄位（小集合衍生）
- `.omit({...})` — 移除敏感 / 內部欄位
- `.partial()` — 全部變 optional（PATCH 端點常用）
- `.required()` — 把 optional 全部變必填（罕用）

## 例外

衍生 schema 的欄位限制與原 schema 顯著不同時（例如 admin update 比 user update 多一倍欄位），分開定義反而清楚。
