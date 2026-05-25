---
rule: di-provider-scope
category: 依賴注入
tags: [di, scope, performance]
---

# 慎用 request-scoped 與 transient provider

> Provider 預設是單例（DEFAULT scope），需要時才用 REQUEST / TRANSIENT，並留意它會往上傳染且影響效能。

## 原因

- 預設單例在整個應用共用一份實例，效能最好，多數 provider 都該維持預設。
- REQUEST-scoped provider 每個請求建立一份，注入它的 provider 也會被迫變成 request-scoped，往上一路傳染，拖慢整體效能。
- 把「每個請求不同的狀態」綁進單例會造成資料外洩到別的請求；反過來，把無狀態服務設成 request-scoped 則是浪費。

## ❌ Bad

```ts
// 無狀態的 service 卻設成 request-scoped，平白增加每請求建構成本
@Injectable({ scope: Scope.REQUEST })
export class PriceCalculator {
  calculate(items: Item[]) {
    return items.reduce((s, i) => s + i.price, 0);
  }
}
```

`PriceCalculator` 沒有任何請求相關狀態，設成 request-scoped 只會讓注入它的鏈路全部變慢。

## ✅ Good

```ts
// 無狀態服務維持預設單例
@Injectable()
export class PriceCalculator {
  calculate(items: Item[]) {
    return items.reduce((sum, item) => sum + item.price, 0);
  }
}

// 真正需要每請求資料時，才用 request-scoped，並接受傳染成本
@Injectable({ scope: Scope.REQUEST })
export class RequestContext {
  constructor(@Inject(REQUEST) private readonly req: Request) {}
  get userId() {
    return this.req.user?.id;
  }
}
```

只有真正需要綁定單一請求資料（如 `RequestContext`）才用 REQUEST scope，並理解它會往上傳染。
