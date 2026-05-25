---
rule: guard-authz
category: Guard
tags: [guard, auth, authorization, throttler]
---

# 認證與授權用 Guard

> 認證與授權判斷用 Guard 處理，別在 controller 或 service 內手刻權限檢查；rate limiting 用 `@nestjs/throttler` 的 `ThrottlerGuard`。

## 原因

- Guard 在 handler 執行前統一攔截，權限邏輯集中、可重用，不會散落在每個 method。
- 把權限判斷寫進 service 會讓 business logic 混入授權細節，難以測試也難以重用。
- Rate limiting 本質也是請求進入前的 guard 行為，用官方 `ThrottlerGuard` 即可全域或局部套用。

## ❌ Bad

```ts
@Controller('admin')
export class AdminController {
  @Get('stats')
  getStats(@Req() req: Request) {
    // 在 handler 內手刻權限判斷，每個 method 都要重抄一次
    if (req.user?.role !== 'admin') {
      throw new ForbiddenException();
    }
    return this.adminService.stats();
  }
}
```

授權邏輯混在 handler 裡，每個需要管控的 endpoint 都得重複一遍，容易漏。

## ✅ Good

```ts
@Injectable()
export class RolesGuard implements CanActivate {
  constructor(private readonly reflector: Reflector) {}

  canActivate(ctx: ExecutionContext): boolean {
    const required = this.reflector.get<string[]>('roles', ctx.getHandler());
    if (!required) return true;
    const { user } = ctx.switchToHttp().getRequest();
    return required.includes(user?.role);
  }
}

@Controller('admin')
@UseGuards(RolesGuard)
export class AdminController {
  @Get('stats')
  @SetMetadata('roles', ['admin'])
  getStats() {
    return this.adminService.stats();
  }
}

// rate limiting：全域套用 ThrottlerGuard
@Module({
  imports: [ThrottlerModule.forRoot([{ ttl: 60_000, limit: 100 }])],
  providers: [{ provide: APP_GUARD, useClass: ThrottlerGuard }],
})
export class AppModule {}
```

授權集中在 `RolesGuard`，handler 只用 metadata 宣告需要的角色。rate limiting 交給 `ThrottlerGuard` 全域處理。
