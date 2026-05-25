---
rule: error-path-for-nested
category: 錯誤處理
tags: [error, path, nested]
---

# 多層欄位錯誤靠 `issue.path` 對應欄位

> `ZodIssue.path` 是陣列，描述出錯欄位的完整路徑（包含 nested object key、array index、union branch）。沒有 path 就無法把錯誤對到正確欄位。

## 原因

- 直接顯示 `issue.message` 而忽略 `path`，使用者只看到「太短」但不知道是哪個欄位
- `path` 在 nested 結構與陣列裡是必要資訊
- 自訂 refine 時忘了帶 `path` 會讓錯誤掛在 object root，與其他欄位混在一起

## ❌ Bad

```ts
import { z } from "zod";

const result = Schema.safeParse(input);
if (!result.success) {
  for (const issue of result.error.issues) {
    showError(issue.message);
  }
}
```

10 個欄位錯都顯示「Required」，使用者完全不知道是哪 10 個。

## ✅ Good

```ts
import { z } from "zod";

const result = Schema.safeParse(input);
if (!result.success) {
  for (const issue of result.error.issues) {
    const fieldPath = issue.path.join(".");
    setFieldError(fieldPath, issue.message);
  }
}
```

陣列 / nested 範例：

```ts
const Order = z.object({
  items: z.array(z.object({ sku: z.string().min(1) })),
});

const result = Order.safeParse({ items: [{ sku: "" }, { sku: "" }] });
result.error.issues[0].path;
```

對應的 UI key 可以是 `items.0.sku` / `items.1.sku`。

## 例外

只有單一欄位的 schema（純 `z.string()`）路徑為空陣列是正常的，這時直接顯示 message 即可。
