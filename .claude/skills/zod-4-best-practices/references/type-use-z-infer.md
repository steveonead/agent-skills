---
rule: type-use-z-infer
category: 型別推斷
tags: [type, inference, dry]
---

# TS 型別一律用 `z.infer<typeof S>`

> Schema 是唯一真相來源。不要手寫對應的 TypeScript interface，否則兩邊一定會 drift。

## 原因

- Zod 的核心設計優勢在於 schema-first inference，重新手寫 interface 等於放棄這個好處
- Schema 改了 type 沒改（或反之）是真實 bug 來源，過 review 也常常漏看
- `z.infer` 同時保留 transform、refine、coerce 後的最終型別

## ❌ Bad

```ts
import { z } from "zod";

const UserSchema = z.object({
  id: z.uuid(),
  email: z.email(),
  age: z.number().int(),
});

interface User {
  id: string;
  email: string;
  age: number;
}

function createUser(user: User) {}
```

`UserSchema` 之後加欄位、改成 nullable，`User` interface 沒跟上。

## ✅ Good

```ts
import { z } from "zod";

const UserSchema = z.object({
  id: z.uuid(),
  email: z.email(),
  age: z.number().int(),
});

type User = z.infer<typeof UserSchema>;

function createUser(user: User) {}
```

慣例上同檔同時 export schema 與 type：

```ts
export const UserSchema = z.object({ ... });
export type User = z.infer<typeof UserSchema>;
```

## 例外

對外發佈 SDK / library 時可能需要手寫 type 以避免把 Zod 變成 peer dependency。這時手寫 type 並用測試確保兩邊同步。
