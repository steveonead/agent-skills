---
rule: validation-global-zod-pipe
category: 驗證（Zod 整合）
tags: [validation, zod, pipe, nestjs-zod]
---

# 全域註冊 ZodValidationPipe

> 用 `APP_PIPE` 全域註冊 `nestjs-zod` 的 `ZodValidationPipe`，讓所有 `@Body()`、`@Query()`、`@Param()` 自動以對應 Zod DTO 驗證。

## 原因

- 沒有註冊 `ZodValidationPipe`，`createZodDto` 產出的 DTO 不會真正驗證輸入，型別看起來對、實際沒擋。
- 透過 `APP_PIPE` 全域註冊，每個 endpoint 都自動驗證，不必每個 handler 各自 `@UsePipes`。
- 集中設定也方便日後統一調整錯誤行為。

## ❌ Bad

```ts
@Controller('users')
export class UsersController {
  @Post()
  // 沒有 ZodValidationPipe，CreateUserDto 的 schema 不會被執行
  create(@Body() body: CreateUserDto) {
    return this.usersService.create(body);
  }
}
```

少了 pipe，輸入完全沒被 Zod 驗證，非法資料會直接進到 service。

## ✅ Good

```ts
import { APP_PIPE } from '@nestjs/core';
import { ZodValidationPipe } from 'nestjs-zod';

@Module({
  providers: [{ provide: APP_PIPE, useClass: ZodValidationPipe }],
})
export class AppModule {}
```

全域掛上 `ZodValidationPipe` 後，凡是參數型別為 Zod DTO 的 `@Body/@Query/@Param`，都會在進入 handler 前自動驗證。
