---
rule: v4-error-param-unified
category: Zod 4 API 強制
tags: [v4, error, message, errorMap, deprecated]
---

# 自訂錯誤統一用 `error` 參數

> Zod 4 把 `invalid_type_error` / `required_error` / `message` / `errorMap` 四個分散的 API 統一為單一 `error` 參數，可接受字串或 `(issue) => string` 函式。

## 原因

- v3 四個 API 互相覆蓋、優先級不明，常造成「為什麼錯誤訊息沒換掉」的困惑
- v4 統一為 `error`，行為一致；同時支援靜態字串與動態函式
- `invalid_type_error` / `required_error` 不對應任何 Zod 實際 issue code（沒有 `required` issue code），是 v3 的設計遺憾

## ❌ Bad

```ts
import { z } from "zod";

const Name = z.string({
  required_error: "姓名為必填",
  invalid_type_error: "姓名必須是字串",
});

const Email = z.email({
  message: "Email 格式錯誤",
});

const schema = z.string().min(8, { message: "至少 8 個字元" });

const config = z.object({...}, {
  errorMap: (issue, ctx) => ({ message: "壞掉了" }),
});
```

## ✅ Good

```ts
import { z } from "zod";

const Name = z.string({
  error: (issue) =>
    issue.input === undefined ? "姓名為必填" : "姓名必須是字串",
});

const Email = z.email({ error: "Email 格式錯誤" });

const Password = z.string().min(8, { error: "至少 8 個字元" });

const config = z.config({
  customError: (issue) => {
    if (issue.code === "too_small") return "太短";
    return undefined;
  },
});
```

`error` 函式回傳 `undefined` 代表交給下一個 error map 處理，方便組合多層客製訊息。

## 例外

全站統一 i18n 訊息時，用 `z.config({ locale: z.locales.zhTW() })` 設定 locale，個別 schema 不再覆寫 `error`。
