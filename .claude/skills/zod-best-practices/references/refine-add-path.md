---
rule: refine-add-path
category: Refine 與 Transform
tags: [refine, path, error]
---

# `.refine()` 附上 `path`

> 物件 schema 的 `.refine()` 預設把錯誤掛在物件 root，UI 無法定位到具體欄位。寫 refine 時都應該帶上 `path`。

## 原因

- 表單 UI 靠 `path` 把錯誤訊息塞到欄位旁；root level 錯誤等於沒有顯示位置
- `treeifyError()` 也是依 `path` 收斂，沒帶 path 就會堆在 root 拿不到欄位錯
- 連最常見的「兩次密碼不一致」場景，沒寫 path 都會出問題

## ❌ Bad

```ts
import { z } from "zod";

const Form = z.object({
  password: z.string().min(8),
  confirm: z.string(),
}).refine(
  (val) => val.password === val.confirm,
  { error: "兩次密碼不一致" },
);
```

UI 無法對應到 `confirm` 欄位的錯誤，只能在表單最上方顯示一條無法定位欄位的錯誤訊息。

## ✅ Good

```ts
import { z } from "zod";

const Form = z.object({
  password: z.string().min(8),
  confirm: z.string(),
}).refine(
  (data) => data.password === data.confirm,
  {
    error: "兩次密碼不一致",
    path: ["confirm"],
  },
);

const DateRange = z.object({
  start: z.iso.date(),
  end: z.iso.date(),
}).refine(
  (range) => range.start <= range.end,
  {
    error: "結束日期必須晚於開始日期",
    path: ["end"],
  },
);
```

`.superRefine()` 也一樣，`ctx.addIssue({ path: [...] })`：

```ts
const Schema = z.object({
  items: z.array(z.object({ qty: z.number() })),
}).superRefine((order, ctx) => {
  order.items.forEach((item, index) => {
    if (item.qty <= 0) {
      ctx.addIssue({
        code: "custom",
        message: "數量需大於 0",
        path: ["items", index, "qty"],
      });
    }
  });
});
```

## 例外

refine 確實對應整個物件層級的錯誤（例如「整體 payload 不符合業務規則」）才不加 path，但實務上幾乎都能對應到某個欄位。
