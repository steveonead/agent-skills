---
rule: di-constructor-injection
category: 依賴注入
tags: [di, constructor-injection, module-ref]
---

# 用 constructor injection，別當 service locator

> 預設用 constructor injection 取得依賴，不要手動 `new`，也不要把 `ModuleRef` 當 service locator 來隱藏依賴。

## 原因

- Constructor injection 讓依賴顯性出現在簽章上，看一眼就知道這個 class 需要什麼，也方便測試替換。
- 手動 `new` 會繞過 DI 容器，拿不到單例與生命週期管理，破壞封裝。
- 用 `ModuleRef.get()` 到處撈 provider 是 service locator 反模式：依賴被藏起來，編譯期看不出耦合，測試也難以注入假物件。

## ❌ Bad

```ts
@Injectable()
export class OrdersService {
  constructor(private readonly moduleRef: ModuleRef) {}

  async create(dto: CreateOrderDto) {
    // 用 service locator 撈依賴，依賴被藏起來
    const payments = this.moduleRef.get(PaymentsService, { strict: false });
    const mailer = new MailerService(); // 又手動 new，繞過 DI
    // ...
  }
}
```

依賴藏在方法內部，從 constructor 看不出 `OrdersService` 其實需要 `PaymentsService` 與 `MailerService`。

## ✅ Good

```ts
@Injectable()
export class OrdersService {
  constructor(
    private readonly payments: PaymentsService,
    private readonly mailer: MailerService,
  ) {}

  async create(dto: CreateOrderDto) {
    // 直接用注入進來的依賴
  }
}
```

依賴全部列在 constructor，一目了然，測試時用 `overrideProvider` 就能替換。

## 例外

確實需要動態解析（如外掛系統、依執行期條件取得不同 provider）時，`ModuleRef` 是正當工具，但要明確標示這是刻意的動態解析，而非用來隱藏依賴。
