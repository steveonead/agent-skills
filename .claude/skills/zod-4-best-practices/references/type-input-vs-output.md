---
rule: type-input-vs-output
category: 型別推斷
tags: [type, transform, input, output]
---

# 含 transform 時：輸入端用 `z.input`、輸出端用 `z.infer`

> 一旦 schema 有 `.transform()` / `.pipe()` / `.coerce()`，輸入型別與輸出型別會不同。用錯一邊會讓 TypeScript 騙你。

## 原因

- `z.infer<typeof S>` = `z.output<typeof S>`，是 parse **之後** 的型別
- `z.input<typeof S>` 是 parse **之前** 的型別
- 用 output 型別去描述「呼叫端要傳的資料」會誤導：呼叫端傳的是 input

## ❌ Bad

```ts
import { z } from "zod";

const Schema = z.object({
  createdAt: z.iso.datetime().transform((s) => new Date(s)),
  count: z.coerce.number(),
});

type Payload = z.infer<typeof Schema>;
// { createdAt: Date; count: number }

function send(payload: Payload) {
  return fetch("/api", { body: JSON.stringify(payload) });
}
```

呼叫端被誤導，以為要傳 `Date`，實際 API 收的是 ISO string。

## ✅ Good

```ts
import { z } from "zod";

const Schema = z.object({
  createdAt: z.iso.datetime().transform((isoString) => new Date(isoString)),
  count: z.coerce.number(),
});

type Input = z.input<typeof Schema>;
type Output = z.infer<typeof Schema>;

function send(payload: Input) {
  return fetch("/api", { body: JSON.stringify(payload) });
}

function handleParsed(data: Output) {
  data.createdAt.getFullYear();
}
```

判斷準則：
- 描述「呼叫端輸入」、「API request body」 → `z.input`
- 描述「parse 完之後的內部資料」、「business logic 拿到的物件」 → `z.infer`

## 例外

Schema 完全沒有 transform / coerce 時，`z.input` 與 `z.infer` 等價，這時為了一致性仍建議 `z.infer`。
