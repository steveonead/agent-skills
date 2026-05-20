---
rule: v4-default-vs-prefault
category: Zod 4 API 強制
tags: [v4, default, prefault]
---

# 認識 `.default()` 行為變更，必要時用 `.prefault()`

> Zod 4 改變 `.default()` 的套用時機：default 值必須符合 schema 的 **output** 型別，並會在 transform / refine 之前注入。如果需要 v3 的「pre-parse default」行為（default 值是 schema 的 **input**），改用新增的 `.prefault()`。

## 原因

- v3 的 default 行為在 `.transform()` / `.refine()` 鏈中時機混亂，常出現「default 值跑去前面被 transform 改掉」的 bug
- v4 釐清為兩種獨立語意：`.default()` = post-parse default，`.prefault()` = pre-parse default
- 直接從 v3 搬過來而不調整，會在 transform 鏈中拿到型別不符的 default 值

## ❌ Bad

```ts
import { z } from "zod";

const v3Like = z
  .string()
  .transform((s) => s.toUpperCase())
  .default("hello");
```

在 v3 中，`"hello"` 是 string，會先進 transform 變成 `"HELLO"`。
在 v4，`.default()` 要求 default 值符合 **output** 型別，且套用於 transform 之後，原本依賴「default 會被 transform 處理」的程式碼會壞掉。

## ✅ Good

```ts
import { z } from "zod";

const PostParseDefault = z
  .string()
  .transform((text) => text.toUpperCase())
  .default("HELLO");

const PreParseDefault = z
  .string()
  .transform((text) => text.toUpperCase())
  .prefault("hello");
```

選擇準則：
- 想要 default 值直接就是最終輸出 → `.default()`
- 想要 default 值經過 transform / coerce 再輸出 → `.prefault()`

另一個 v4 行為改變：optional 欄位的內層 default 也會套用：

```ts
const Schema = z.object({
  a: z.string().default("tuna").optional(),
});
Schema.parse({});
// v4: { a: "tuna" }
// v3: {}
```

依賴 v3 「key 存在性」的程式碼要一併調整。

## 例外

無。新程式碼直接用 v4 行為；migration 時逐一檢查 `.default()` 是否需要改成 `.prefault()`。
