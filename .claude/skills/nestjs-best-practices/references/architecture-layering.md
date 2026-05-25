---
rule: architecture-layering
category: 模組與分層架構
tags: [architecture, layering, repository, prisma]
---

# 維持 controller → service → repository 分層

> 各層職責分明：controller 傳輸、service 業務邏輯（單一職責）、repository 資料存取，且 repository 用 `select`/`include` 塑形查詢避免 N+1。

## 原因

- 分層讓每一層可獨立測試與替換，service 不直接綁死特定 ORM 細節。
- 每個 service 維持單一職責，避免一個 service 同時做訂單、付款、通知，難以維護與測試。
- 資料存取集中在 repository，能在這層統一處理查詢效率，例如一次帶出關聯資料，避免在迴圈裡逐筆查（N+1）。

## ❌ Bad

```ts
@Injectable()
export class OrdersService {
  constructor(private readonly prisma: PrismaService) {}

  async listWithCustomer() {
    const orders = await this.prisma.order.findMany();
    // 在迴圈裡逐筆查 customer，造成 N+1
    return Promise.all(
      orders.map(async (o) => ({
        ...o,
        customer: await this.prisma.customer.findUnique({ where: { id: o.customerId } }),
      })),
    );
  }
}
```

service 直接碰 Prisma 又在迴圈裡逐筆查詢，職責混雜且效能差。

## ✅ Good

```ts
@Injectable()
export class OrderRepository {
  constructor(private readonly prisma: PrismaService) {}

  // 在資料層一次帶出關聯，避免 N+1
  listWithCustomer() {
    return this.prisma.order.findMany({
      include: { customer: true },
    });
  }
}

@Injectable()
export class OrdersService {
  constructor(private readonly orders: OrderRepository) {}

  listWithCustomer() {
    return this.orders.listWithCustomer();
  }
}
```

查詢塑形集中在 repository，用 `include` 一次帶出關聯。service 只專注訂單相關業務邏輯，保持單一職責。
