---
rule: parse-async-for-async-refinements
category: 解析與驗證
tags: [parse, async, refinement]
---

# 含 async refine 必用 `parseAsync` / `safeParseAsync`

> Schema 內只要有任何 async `.refine()` / `.transform()`，就必須用 `parseAsync()` 或 `safeParseAsync()`。同步版本會 throw `Async refinement encountered during synchronous parse`。

## 原因

- Zod 的同步 / async parse 是兩條獨立的 code path
- 在 async refine 用同步 parse 不會「等」async 完成，會直接 throw
- 這個錯誤通常 dev 環境才會浮出，production 流量大時才爆炸的機率很高

## ❌ Bad

```ts
import { z } from "zod";

const Username = z.string().refine(
  async (name) => !(await isTaken(name)),
  { error: "已被使用" },
);

function handle(input: unknown) {
  return Username.safeParse(input);
}
```

`safeParse()` 看到 async refinement 直接 throw，外層 success / error 分支拿不到正常結果。

## ✅ Good

```ts
import { z } from "zod";

const Username = z.string().refine(
  async (name) => !(await isTaken(name)),
  { error: "已被使用" },
);

async function handle(input: unknown) {
  const result = await Username.safeParseAsync(input);
  if (!result.success) {
    return { ok: false, errors: z.treeifyError(result.error) };
  }
  return { ok: true, data: result.data };
}
```

判斷準則：
- Schema 內有 `async (input) => ...` → `parseAsync` / `safeParseAsync`
- 全部同步 → `parse` / `safeParse`
- 不確定 → 預設 `safeParseAsync`，是 superset

## 例外

純效能敏感、確認 schema 無 async 的 hot path 才用同步版本。
