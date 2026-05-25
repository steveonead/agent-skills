---
rule: schema-avoid-optional-abuse
category: Schema 定義
tags: [schema, optional, design]
---

# 不要濫用 `.optional()`

> 把欄位標成 `.optional()` 是為了「真的可以省略」，不是為了避免 validation error。每個 optional 都是呼叫端的 null check 成本。

## 原因

- 過多 optional 讓 schema 等於「什麼都收」，validation 失去意義
- 呼叫端被迫到處寫 `if (x !== undefined)`，擴散至整個 codebase
- TypeScript 推出來的型別與真實意圖不一致，是 bug 溫床

## ❌ Bad

```ts
import { z } from "zod";

const CreateUserRequest = z.object({
  email: z.email().optional(),
  password: z.string().min(8).optional(),
  name: z.string().optional(),
  role: z.enum(["admin", "user"]).optional(),
});
```

建立使用者時，email 與 password 應為必填欄位；全標為 optional 使此 schema 失去驗證效果。

## ✅ Good

```ts
import { z } from "zod";

const CreateUserRequest = z.object({
  email: z.email(),
  password: z.string().min(8),
  name: z.string().min(1),
  role: z.enum(["admin", "user"]).default("user"),
});
```

判斷準則：
- 必填 → 不加 `.optional()`
- 沒填就用預設值 → 用 `.default()`
- 真的允許省略且呼叫端要顯式處理 → 用 `.optional()`
- API 回傳值的 `null` → 用 `.nullable()`，不要與 optional 混用

## 例外

部分更新（PATCH 端點）用 `Schema.partial()` 一次標記所有欄位 optional，這是合理用法，不算濫用。
