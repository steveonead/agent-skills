---
rule: architecture-avoid-global-module
category: 模組與分層架構
tags: [architecture, module, global]
---

# 少用 @Global()

> 除了少數真正全域共用的基礎設施（設定、資料庫連線），優先用 `imports` 明確宣告依賴，不要輕易使用 `@Global()`。

## 原因

- `@Global()` 讓 provider 隨處可注入，依賴關係從程式碼上看不出來，後續難以追蹤誰用了什麼。
- 過度全域化會讓模組間耦合隱形增加，重構時不知道牽動範圍。
- 用 `imports` 明確宣告，依賴在模組定義上一目了然，也比較好做測試替換。

## ❌ Bad

```ts
@Global()
@Module({
  providers: [UsersService],
  exports: [UsersService],
})
export class UsersModule {}
```

把領域模組設成全域，任何地方都能注入 `UsersService`，依賴關係從此隱形。

## ✅ Good

```ts
@Module({
  providers: [UsersService],
  exports: [UsersService],
})
export class UsersModule {}

@Module({
  imports: [UsersModule], // 需要才明確 import
  providers: [OrdersService],
})
export class OrdersModule {}
```

領域模組不設全域，需要的模組明確 `imports`。`@Global()` 只留給設定、資料庫連線這類真正無所不在的基礎設施。

## 例外

`ConfigModule`、`PrismaModule` 等全應用共用的基礎設施模組，設成全域可省去大量重複 import，是合理用法。
