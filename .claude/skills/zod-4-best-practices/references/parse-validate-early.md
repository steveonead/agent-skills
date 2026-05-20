---
rule: parse-validate-early
category: 解析與驗證
tags: [parse, boundary, validation, env, json]
---

# 邊界一次驗證，內部信任型別

> 外部資料（HTTP request、JSON.parse 結果、檔案、env var、第三方 API response）一進入系統就 parse 一次。內部模組之間信任 TypeScript 型別，不再重複驗證。

## 原因

- 在 business logic 內部驗證等於髒資料已經傳播到一半才發現
- 邊界驗證讓系統內部型別保證有意義，否則 `z.infer` 推出的型別不可信
- env var、`JSON.parse` 預設都是 `any` / `unknown`，未驗證直接用是 runtime 炸彈

## ❌ Bad

```ts
import { z } from "zod";

app.post("/users", (req, res) => {
  createUser(req.body);
});

function createUser(input: any) {
  const user = CreateUserSchema.parse(input);
  saveUser(user);
}

function saveUser(user: any) {
  const validated = UserSchema.parse(user);
  db.insert(validated);
}

const config = JSON.parse(fs.readFileSync("config.json", "utf8"));
server.listen(config.port);
```

驗證散落多層、env / JSON 未驗證就用。

## ✅ Good

```ts
import { z } from "zod";

const EnvSchema = z.object({
  PORT: z.coerce.number().int().positive(),
  DATABASE_URL: z.url(),
});
const env = EnvSchema.parse(process.env);

const Config = z.object({ port: z.number() });
const config = Config.parse(JSON.parse(fs.readFileSync("config.json", "utf8")));

app.post("/users", (req, res) => {
  const result = CreateUserRequest.safeParse(req.body);
  if (!result.success) return res.status(400).json(z.treeifyError(result.error));
  createUser(result.data);
});

function createUser(input: z.infer<typeof CreateUserRequest>) {
  saveUser(input);
}

function saveUser(user: z.infer<typeof CreateUserRequest>) {
  db.insert(user);
}
```

啟動時驗證 env / config 失敗就 crash，符合 fail-fast。

## 例外

跨服務的「不信任邊界」內部仍要驗證一次，例如從 message queue 拉回來的訊息即使已經被上游 service 寫過 schema，也要再驗一次。
