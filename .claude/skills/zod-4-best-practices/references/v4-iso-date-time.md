---
rule: v4-iso-date-time
category: Zod 4 API 強制
tags: [v4, datetime, iso, deprecated]
---

# 日期時間用 `z.iso.*`

> Zod 4 把日期時間格式集中到 `z.iso` namespace，`z.string().datetime()` 等寫法已 deprecate。

## 原因

- `z.iso.*` 表達意圖更明確，一看就知道驗證 ISO 8601 格式
- 與其他字串格式（`z.email()` 等）的 top-level 設計一致
- Zod 3 的 `z.string().datetime()` 在 v4 已 deprecate

## ❌ Bad

```ts
import { z } from "zod";

const Event = z.object({
  startAt: z.string().datetime(),
  date: z.string().date(),
  time: z.string().time(),
  duration: z.string().duration(),
});
```

## ✅ Good

```ts
import { z } from "zod";

const Event = z.object({
  startAt: z.iso.datetime(),
  date: z.iso.date(),
  time: z.iso.time(),
  duration: z.iso.duration(),
});
```

需要加入 timezone offset 限制、精度設定等，沿用相同 API：

```ts
const ServerTimestamp = z.iso.datetime({ offset: true, precision: 3 });
```

## 例外

驗證的不是 ISO 8601 而是自訂日期格式時，用 `z.string().regex(...)` 自定。
