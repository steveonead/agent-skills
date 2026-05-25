---
rule: architecture-thin-controller
category: 模組與分層架構
tags: [architecture, controller, versioning]
---

# Controller 保持輕薄

> Controller 只負責收 request、呼叫 service、回傳 response，business logic 一律放 service；破壞性 API 變更用 `app.enableVersioning()` 管理。

## 原因

- Controller 是傳輸層，混入 business logic 後難以重用，也難以脫離 HTTP 情境測試。
- 邏輯集中在 service，單元測試可以直接測 service，不必每次都走 HTTP。
- 對外 API 有破壞性變更時，用版本機制並存新舊，比在 controller 內塞 if/else 判斷乾淨。

## ❌ Bad

```ts
@Controller('orders')
export class OrdersController {
  constructor(private readonly prisma: PrismaService) {}

  @Post()
  async create(@Body() body: CreateOrderDto) {
    // business logic 直接寫在 controller
    if (body.items.length === 0) throw new BadRequestException('empty');
    const total = body.items.reduce((s, i) => s + i.price * i.qty, 0);
    return this.prisma.order.create({ data: { total, items: body.items } });
  }
}
```

controller 直接碰 Prisma 與計算邏輯，無法重用，也綁死在 HTTP 層。

## ✅ Good

```ts
@Controller({ path: 'orders', version: '1' })
export class OrdersController {
  constructor(private readonly ordersService: OrdersService) {}

  @Post()
  create(@Body() dto: CreateOrderDto) {
    return this.ordersService.create(dto);
  }
}

// main.ts：破壞性變更時用版本並存
app.enableVersioning({ type: VersioningType.URI });
```

controller 只做轉發，邏輯落在 `OrdersService`。需要破壞性變更時，新版掛 `version: '2'`，舊版繼續服務既有 client。
