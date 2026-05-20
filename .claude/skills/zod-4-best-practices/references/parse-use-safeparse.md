---
rule: parse-use-safeparse
category: 解析與驗證
tags: [parse, safeParse, error-handling]
---

# 使用者輸入用 `safeParse()`

> `parse()` 失敗會 throw `ZodError`；對使用者輸入用 `parse()` 等於每次驗證失敗都拋例外。應該預設 `safeParse()`，並走 success / error 分支。

## 原因

- 驗證失敗在「使用者輸入」場景是預期行為，不該用 exception flow 處理
- 未捕捉的 `ZodError` 在 server 端會變成 500，可能把 stack trace 與內部欄位漏給客戶端
- `safeParse()` 回傳 discriminated union，TypeScript 會強制處理兩個分支

## ❌ Bad

```ts
import { z } from "zod";

function handleLogin(input: unknown) {
  const data = LoginSchema.parse(input);
  return authenticate(data);
}
```

任何欄位不符都會炸掉 handler，要靠最外層 try/catch 接，邏輯散落各處。

## ✅ Good

```ts
import { z } from "zod";

function handleLogin(input: unknown) {
  const result = LoginSchema.safeParse(input);
  if (!result.success) {
    return { ok: false, errors: z.treeifyError(result.error) };
  }
  return { ok: true, data: authenticate(result.data) };
}
```

## 例外

兩種場景可以保留 `parse()`：
- **內部不可能失敗** 的解析（例如剛 build 的 object 自我驗證）—驗證失敗代表 bug，throw 是合理的
- **啟動時驗證 env / config**—失敗就直接讓 process crash 反而是想要的行為
