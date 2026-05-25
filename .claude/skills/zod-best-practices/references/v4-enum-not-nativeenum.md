---
rule: v4-enum-not-nativeenum
category: Zod 4 API 強制
tags: [v4, enum, nativeEnum, deprecated]
---

# 用 `z.enum()`，不要用 `z.nativeEnum()`

> Zod 4 的 `z.enum()` 統一處理 string literal 與 TypeScript enum，`z.nativeEnum()` 已 deprecate。

## 原因

- v4 把 `z.enum()` 升級成可吃 TypeScript enum 物件，原本 `z.nativeEnum()` 的能力被併入
- 維護兩個 API 增加選擇成本，且 `z.nativeEnum()` 名稱本身就暗示「特殊用途」，誤導 v4 使用者
- 統一 API 後 enum 的 inferred type 更穩定

## ❌ Bad

```ts
import { z } from "zod";

enum Role {
  Admin = "admin",
  User = "user",
}

const RoleSchema = z.nativeEnum(Role);

const Status = z.enum(["draft", "published"]);
```

## ✅ Good

```ts
import { z } from "zod";

enum Role {
  Admin = "admin",
  User = "user",
}

const RoleSchema = z.enum(Role);

const Status = z.enum(["draft", "published"]);

type Status = z.infer<typeof Status>;
```

`z.enum()` 也接受 readonly array 與 const-asserted tuple：

```ts
const colors = ["red", "green", "blue"] as const;
const Color = z.enum(colors);
```

## 例外

需要與外部產生的純物件（非 TS enum）對應，且該物件結構不穩定時，仍可保留 `z.nativeEnum()` 直到該外部依賴穩定。但新程式碼一律用 `z.enum()`。
