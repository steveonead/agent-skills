---
rule: architecture-circular-dependency
category: 模組與分層架構
tags: [architecture, circular-dependency, event-emitter]
---

# 用事件或抽共用模組解循環依賴

> 兩個模組互相依賴時，優先用事件（`@nestjs/event-emitter`）解耦或抽出第三個共用模組，`forwardRef()` 是最後手段。

## 原因

- 循環依賴常導致注入到 `undefined`，是難以察覺的 runtime 隱患。
- `forwardRef()` 只是繞過症狀，沒解決設計問題，而且讓初始化順序變得脆弱。
- A 直接呼叫 B 改成 A 發事件、B 監聽，就能切斷直接依賴；若兩者真的互相需要，通常代表還有第三個職責該獨立成模組。

## ❌ Bad

```ts
@Injectable()
export class UsersService {
  // UsersService 與 OrdersService 互相注入，需要 forwardRef 才不報錯
  constructor(
    @Inject(forwardRef(() => OrdersService))
    private readonly ordersService: OrdersService,
  ) {}

  async deactivate(userId: string) {
    await this.ordersService.cancelAllForUser(userId);
  }
}
```

用 `forwardRef()` 硬接循環依賴，初始化脆弱，設計問題沒被解決。

## ✅ Good

```ts
@Injectable()
export class UsersService {
  constructor(private readonly events: EventEmitter2) {}

  async deactivate(userId: string) {
    // 發事件，不直接呼叫 OrdersService
    this.events.emit('user.deactivated', { userId });
  }
}

@Injectable()
export class OrdersService {
  @OnEvent('user.deactivated')
  async onUserDeactivated({ userId }: { userId: string }) {
    await this.cancelAllForUser(userId);
  }
}
```

`UsersService` 發事件、`OrdersService` 監聽，切斷直接依賴。若邏輯共用且小，也可抽到雙方都 import 的共用模組。

## 例外

少數框架層或本來就互相緊耦合的設計，在抽不開的情況下，`forwardRef()` 可作為最後手段，但要附註說明原因。
