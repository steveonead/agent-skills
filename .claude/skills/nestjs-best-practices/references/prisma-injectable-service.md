---
rule: prisma-injectable-service
category: Prisma 整合
tags: [prisma, injectable, singleton]
---

# 把 PrismaClient 包成 @Injectable 的 PrismaService

> 用一個繼承 `PrismaClient` 的 `@Injectable() PrismaService` 單例注入到各 service，不要在各處 `new PrismaClient()`。

## 原因

- 每處 `new PrismaClient()` 都會各開一組連線池，連線數很快就耗盡。
- 包成 NestJS provider 後是整個應用共用一份單例，連線管理交給 DI 容器。
- 集中成 `PrismaService` 後，連線設定、log、生命週期都有單一掛載點。

## ❌ Bad

```ts
@Injectable()
export class UsersService {
  // 每個 service 各自 new 一份，連線池各開一組
  private prisma = new PrismaClient();

  findAll() {
    return this.prisma.user.findMany();
  }
}
```

每個 service 自己建 client，連線數失控，也無法統一管理生命週期。

## ✅ Good

```ts
@Injectable()
export class PrismaService extends PrismaClient {}

@Module({
  providers: [PrismaService],
  exports: [PrismaService],
})
export class PrismaModule {}

@Injectable()
export class UsersService {
  constructor(private readonly prisma: PrismaService) {}

  findAll() {
    return this.prisma.user.findMany();
  }
}
```

`PrismaService` 是單例 provider，各 service 注入同一份，連線池統一管理。`PrismaModule` 可設成全域供全應用使用。
