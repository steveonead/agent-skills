---
rule: interceptor-cross-cutting
category: Interceptor
tags: [interceptor, cross-cutting, logging, timeout]
---

# 橫切關注用 Interceptor

> logging、response 包裝、timeout、cache 等橫切關注用 Interceptor 統一處理，別把這些重複邏輯散落在每個 handler。

## 原因

- Interceptor 能在 handler 前後插入邏輯，適合處理跨多個 endpoint 的共通行為。
- 把 response 統一包裝、計時、逾時控制散寫在每個 handler，會大量重複且容易不一致。
- 集中在 interceptor 後，要調整共通行為只改一處。

## ❌ Bad

```ts
@Controller('orders')
export class OrdersController {
  @Get()
  async list() {
    const start = Date.now();
    const data = await this.ordersService.list();
    // 每個 handler 各自包裝 response、各自計時
    console.log(`list took ${Date.now() - start}ms`);
    return { data, success: true };
  }
}
```

計時與 response 包裝在每個 handler 重複，格式容易飄移，也難以統一調整。

## ✅ Good

```ts
@Injectable()
export class TransformInterceptor<T> implements NestInterceptor<T, { data: T }> {
  intercept(ctx: ExecutionContext, next: CallHandler): Observable<{ data: T }> {
    const start = Date.now();
    return next.handle().pipe(
      map((data) => ({ data, success: true })),
      tap(() => this.logger.log(`${ctx.getHandler().name} took ${Date.now() - start}ms`)),
    );
  }
}

@Module({
  providers: [{ provide: APP_INTERCEPTOR, useClass: TransformInterceptor }],
})
export class AppModule {}

@Controller('orders')
export class OrdersController {
  @Get()
  list() {
    return this.ordersService.list(); // handler 只回業務資料
  }
}
```

response 包裝與計時集中在 interceptor，handler 只專注回傳業務資料，共通行為一處調整全應用生效。
