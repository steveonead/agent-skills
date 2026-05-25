---
rule: v4-uuid-vs-guid
category: Zod 4 API 強制
tags: [v4, uuid, guid]
---

# `z.uuid()` 嚴格、`z.guid()` 寬鬆

> Zod 4 的 `z.uuid()` 嚴格遵循 RFC 9562/4122（要求 variant bits 為 `10`），比 Zod 3 的 `z.string().uuid()` 嚴格。需要 v3 寬鬆語意請改用 `z.guid()`。

## 原因

- v3 的 `z.string().uuid()` 規則寬鬆，會接受不符合 RFC 9562 的「類 UUID」字串
- v4 的 `z.uuid()` 拒絕這類值，從 v3 直接搬過來會多出許多 validation failure
- `z.guid()` 維持寬鬆驗證，給確實只是「UUID-like」格式的場景使用

## ❌ Bad

```ts
import { z } from "zod";

const Id = z.string().uuid();
const old = "00000000-0000-0000-0000-000000000000";
Id.safeParse(old);
```

直接用 `.uuid()` 從 v3 移到 v4，會把過去通過的 nil UUID、版號錯誤的舊資料判為無效。

## ✅ Good

```ts
import { z } from "zod";

const StrictId = z.uuid();
const StrictV7 = z.uuid({ version: "v7" });

const LegacyId = z.guid();
```

判斷準則：
- 新欄位、要求 RFC 9562 合規 → `z.uuid()`
- 既有資料、需要與 v3 行為相容 → `z.guid()`
- 限定版本 → `z.uuid({ version: "v4" | "v7" | ... })`

## 例外

純粹當 token / opaque string 使用、不真的需要 UUID 語意時，用 `z.string().min(...)` 即可，不必選擇 uuid / guid。
