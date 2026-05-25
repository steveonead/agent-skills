---
rule: architecture-module-encapsulation
category: 模組與分層架構
tags: [architecture, module, encapsulation]
---

# 模組只 export 對外需要的 provider

> 模組的 `exports` 就是它的公開 API，只 export 其他模組真正需要的 provider，內部 repository 與細節不外露。

## 原因

- NestJS 模組預設封裝 provider，沒 export 的東西外部注入不到，這是維持邊界的關鍵機制。
- 把 repository、internal helper 一併 export，等於把實作細節公開，其他模組就會繞過 service 直接動資料層。
- 對外只露 service，未來換掉內部實作不會影響到呼叫端。

## ❌ Bad

```ts
@Module({
  controllers: [UsersController],
  providers: [UsersService, UsersRepository],
  // 把 repository 也 export，外部模組能直接注入動資料層
  exports: [UsersService, UsersRepository],
})
export class UsersModule {}
```

`UsersRepository` 被 export 後，其他模組可直接操作 users 資料表，繞過 `UsersService` 的規則，邊界形同虛設。

## ✅ Good

```ts
@Module({
  controllers: [UsersController],
  providers: [UsersService, UsersRepository],
  // 只露 service 當公開 API，repository 留在模組內
  exports: [UsersService],
})
export class UsersModule {}
```

只 export `UsersService`。其他模組要操作 users 一律透過 service，repository 與內部細節留在模組內。
