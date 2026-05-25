---
rule: validation-zod-serializer
category: 驗證（Zod 整合）
tags: [validation, zod, serialization, nestjs-zod]
---

# 用 ZodSerializerInterceptor 控制回應輸出

> 回應序列化用 `nestjs-zod` 的 `ZodSerializerInterceptor` + `@ZodSerializerDto`，按 output schema 塑形回傳資料，避免把 entity 上的敏感欄位整包丟給 client。

## 原因

- service 回傳的物件常帶有 `passwordHash`、內部欄位等不該外洩的資料，直接回傳等於洩漏。
- 用 output schema 序列化，回應只會包含 schema 定義的欄位，多的自動剔除，形成明確的對外契約。
- output DTO 同樣餵給 OpenAPI，文件與實際回應一致。

## ❌ Bad

```ts
@Controller('users')
export class UsersController {
  @Get(':id')
  // 直接回傳 Prisma 撈出來的整筆，passwordHash 等欄位一併外洩
  findOne(@Param('id') id: string) {
    return this.usersService.findById(id);
  }
}
```

整筆 entity 回傳，內部欄位毫無遮蔽地暴露給 client。

## ✅ Good

```ts
import { ZodSerializerInterceptor, ZodSerializerDto } from 'nestjs-zod';
import { APP_INTERCEPTOR } from '@nestjs/core';

const UserResponseSchema = z.object({
  id: z.uuid(),
  username: z.string(),
  email: z.email(),
});
class UserResponseDto extends createZodDto(UserResponseSchema) {}

@Module({
  providers: [{ provide: APP_INTERCEPTOR, useClass: ZodSerializerInterceptor }],
})
export class AppModule {}

@Controller('users')
export class UsersController {
  @Get(':id')
  @ZodSerializerDto(UserResponseDto) // 只輸出 schema 定義的欄位
  findOne(@Param('id') id: string) {
    return this.usersService.findById(id);
  }
}
```

回應依 `UserResponseDto` 序列化，`passwordHash` 這類未列在 schema 的欄位會被剔除，對外契約清楚且安全。
