---
rule: v4-top-level-string-formats
category: Zod 4 API 強制
tags: [v4, string, format, deprecated]
---

# 字串格式用 top-level 函式

> Zod 4 把 `.email()` / `.url()` / `.uuid()` 等字串格式從 `z.string()` 的 method 升級為 top-level 函式，method form 已 deprecate，下一個主版本會移除。

## 原因

- `z.email()` 比 `z.string().email()` 更短，且 tree-shake 表現更好
- Zod 4 把這些格式實作為 `ZodString` 的 subclass，top-level 函式才是正規入口
- Zod 4 規劃在下一個主版本移除 method form

## ❌ Bad

```ts
import { z } from "zod";

const User = z.object({
  email: z.string().email(),
  homepage: z.string().url(),
  id: z.string().uuid(),
  apiKey: z.string().jwt(),
  avatar: z.string().base64(),
});
```

method form 在 v4 仍可用但已 deprecate，IDE 會顯示刪除線；同時失去 tree-shake 優勢。

## ✅ Good

```ts
import { z } from "zod";

const User = z.object({
  email: z.email(),
  homepage: z.url(),
  id: z.uuid(),
  apiKey: z.jwt(),
  avatar: z.base64(),
});
```

top-level 函式仍可串 `.min()` / `.max()` 等 string method，因為回傳的還是 `ZodString` 的 subclass：

```ts
const Email = z.email().max(255);
const Url = z.url().startsWith("https://");
```

## 例外

字串本身需要先做其他驗證再判斷格式時（罕見）仍可用 method form，但通常透過 `.refine()` 或 `.pipe()` 表達更清楚。
