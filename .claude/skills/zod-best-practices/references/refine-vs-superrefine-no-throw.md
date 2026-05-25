---
rule: refine-vs-superrefine-no-throw
category: Refine 與 Transform
tags: [refine, superRefine, error]
---

# 多重錯誤用 `.superRefine()`；refine 內 return false 不 throw

> 只需要 yes / no 判斷時用 `.refine()`，且回傳 boolean 不 throw。需要報多個錯誤、客製 issue code 或定位到子欄位時用 `.superRefine()`。

## 原因

- `.refine()` 內 throw 會直接中斷整個驗證，後面 issue 收集不到
- `.refine()` 一次只能產生一個 issue；複雜情境用它會擠不出多個錯誤
- `.superRefine()`（v4 也常見 `.check()` 形式）透過 `ctx.addIssue()` 累積錯誤，並能加 `path`

## ❌ Bad

```ts
import { z } from "zod";

const Password = z.string().refine((val) => {
  if (val.length < 8) throw new Error("太短");
  if (!/[A-Z]/.test(val)) throw new Error("需要大寫");
  return true;
});

const Form = z.object({
  password: z.string(),
  confirm: z.string(),
}).refine(
  (val) => val.password === val.confirm,
  { error: "兩次密碼不一致" },
);
```

第一個錯就 throw，使用者看不到所有 issue；confirm 不符的錯誤掛在 root，UI 無法顯示在欄位旁。

## ✅ Good

```ts
import { z } from "zod";

const Password = z.string().superRefine((password, ctx) => {
  if (password.length < 8) {
    ctx.addIssue({ code: "custom", message: "至少 8 個字元" });
  }
  if (!/[A-Z]/.test(password)) {
    ctx.addIssue({ code: "custom", message: "需要至少一個大寫" });
  }
});

const Form = z.object({
  password: z.string(),
  confirm: z.string(),
}).superRefine((data, ctx) => {
  if (data.password !== data.confirm) {
    ctx.addIssue({
      code: "custom",
      message: "兩次密碼不一致",
      path: ["confirm"],
    });
  }
});

const Age = z.number().refine((age) => age >= 18, {
  error: "需要年滿 18 歲",
});
```

判斷準則：
- 單一條件、單一錯誤訊息 → `.refine()`，回傳 boolean
- 多個獨立規則或要定位子欄位 → `.superRefine()`，用 `ctx.addIssue()`

## 例外

確實只想中斷後續驗證（例如資源真的不可用）才用 `ctx.addIssue({ fatal: true })` 加 `return z.NEVER`，不要直接 throw。
