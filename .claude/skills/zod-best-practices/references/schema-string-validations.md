---
rule: schema-string-validations
category: Schema 定義
tags: [schema, string, validation, security]
---

# 字串一律加上 `min` / `max` / `regex` / format

> 純 `z.string()` 等於「任意長度的任意字串」，包含空字串、超長字串、特殊字元。每個字串欄位都應該加上明確的長度與格式限制。

## 原因

- 沒加限制的字串會讓空字串、長度 100 萬的字串、含 NULL byte 的字串通過驗證
- 後續資料庫欄位、UI 顯示、API serialization 都可能炸掉
- 對攻擊面而言，未限制長度的字串是常見 DoS / injection 入口

## ❌ Bad

```ts
import { z } from "zod";

const Profile = z.object({
  username: z.string(),
  bio: z.string(),
  websiteUrl: z.string(),
  phoneNumber: z.string(),
});
```

空字串、長度幾 MB、亂碼一律通過。

## ✅ Good

```ts
import { z } from "zod";

const Profile = z.object({
  username: z
    .string()
    .min(3, { error: "至少 3 個字元" })
    .max(32)
    .regex(/^[a-z0-9_]+$/, { error: "只允許小寫英數與底線" }),
  bio: z.string().trim().max(500),
  websiteUrl: z.url().max(2048),
  phoneNumber: z.e164(),
});
```

常見模式：
- 短文字 → `.min(1).max(N)`
- 多行文字 → `.trim().max(N)`
- 電話 → `z.e164()`
- 網址 → `z.url().max(2048)`
- 標識符（slug、username）→ 加 `.regex()`

## 例外

純粹當不透明 token 轉發（例如 third-party token），且明確知道格式無法控制時，加上 `.max()` 防 DoS 即可，可以不加 regex。
