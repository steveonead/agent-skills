---
rule: parse-handle-all-issues
category: 解析與驗證
tags: [parse, error, ux]
---

# 顯示時彙整 `error.issues`，不只取第一個

> Zod 預設一次回傳所有違反規則的 issue。只顯示第一個錯誤等於強迫使用者修一次送一次，是常見的 UX 失誤。

## 原因

- `result.error.issues` 是陣列，每個 issue 對應一個欄位 / 一個違反規則
- 表單通常有多個欄位同時錯，一次顯示全部能讓使用者一次修完
- 自己只看 `issues[0]` 等於把這個能力丟掉

## ❌ Bad

```ts
import { z } from "zod";

const result = FormSchema.safeParse(input);
if (!result.success) {
  alert(result.error.issues[0].message);
}
```

10 個欄位錯，使用者要送 10 次。

## ✅ Good

```ts
import { z } from "zod";

const result = FormSchema.safeParse(input);
if (!result.success) {
  const fieldErrors = z.treeifyError(result.error);
  showFormErrors(fieldErrors);
}
```

或自行遍歷：

```ts
if (!result.success) {
  for (const issue of result.error.issues) {
    setFieldError(issue.path.join("."), issue.message);
  }
}
```

## 例外

CLI / batch script 早期失敗本來就「停在第一個錯誤」是合理 UX，這時取 `issues[0]` 是有意的設計選擇，不是失誤。
