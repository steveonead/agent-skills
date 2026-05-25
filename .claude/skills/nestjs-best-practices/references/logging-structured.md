---
rule: logging-structured
category: Logging
tags: [logging, structured, pino]
---

# 用結構化 logging，禁裸 console.log

> 用 NestJS 內建 `Logger` 或 `nestjs-pino` 做結構化 logging，帶上 context 與結構化欄位，不要散落裸 `console.log`。

## 原因

- `console.log` 沒有 log level、沒有 context、輸出非結構化，正式環境難以過濾與檢索。
- NestJS `Logger` 自帶 context 標籤與 level，能跟著應用的 log 設定走。
- `nestjs-pino` 輸出 JSON，搭配 request id 等欄位，方便 log 聚合系統解析與查詢。

## ❌ Bad

```ts
@Injectable()
export class PaymentService {
  async charge(orderId: string) {
    console.log('charging order', orderId); // 無 level、無 context、非結構化
    // ...
    console.log('done');
  }
}
```

裸 `console.log` 無法分級與過濾，正式環境的 log 雜亂且難以追查。

## ✅ Good

```ts
@Injectable()
export class PaymentService {
  private readonly logger = new Logger(PaymentService.name);

  async charge(orderId: string) {
    this.logger.log({ msg: 'charging order', orderId });
    try {
      // ...
      this.logger.log({ msg: 'charge succeeded', orderId });
    } catch (error) {
      this.logger.error({ msg: 'charge failed', orderId, error });
      throw error;
    }
  }
}
```

用帶 context 的 `Logger`，log 有 level、有結構化欄位。需要 JSON 輸出與 request 關聯時改用 `nestjs-pino`。
