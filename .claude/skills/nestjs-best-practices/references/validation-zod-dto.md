---
rule: validation-zod-dto
category: 驗證（Zod 整合）
tags: [validation, zod, dto, nestjs-zod]
---

# 用 createZodDto 從 Zod schema 建 DTO

> DTO 用 `nestjs-zod` 的 `createZodDto(schema)` 從 Zod schema 產生，取代 class-validator + class-transformer 的 class DTO，一份 schema 同時供驗證、型別與 OpenAPI 使用。

## 原因

- 一份 Zod schema 同時提供 runtime 驗證、compile-time 型別與 OpenAPI schema，三者永遠同步，不會型別與驗證規則各寫一份而對不上。
- 專案既然用 Zod 4 做型別驗證，DTO 也走 Zod 才一致，不必再維護 class-validator 的 decorator。
- `createZodDto` 產出的是標準 class，能直接當 `@Body()` 等參數型別使用。

> 此處只談如何把 schema 接進 NestJS，不涉及 schema 本身的寫法（`z.email()`、`z.uuid()`、`.optional()` 等）。

## ❌ Bad

```ts
// 用 class-validator 維護一份 decorator，型別與規則分離
export class CreateUserDto {
  @IsString()
  @MinLength(3)
  username: string;

  @IsEmail()
  email: string;
}
```

驗證規則寫在 decorator、型別寫在欄位，兩者各自維護，與專案的 Zod 體系不一致。

## ✅ Good

```ts
import { createZodDto } from 'nestjs-zod';
import { z } from 'zod';

const CreateUserSchema = z.object({
  username: z.string().min(3),
  email: z.email(),
});

export class CreateUserDto extends createZodDto(CreateUserSchema) {}
```

schema 是唯一事實來源，`CreateUserDto` 同時帶有型別、驗證規則與 OpenAPI 定義。要衍生其他 DTO 可用 `CreateUserDto.schema.omit({ ... })` 組合。
