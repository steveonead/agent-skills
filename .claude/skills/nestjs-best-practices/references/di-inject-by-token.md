---
rule: di-inject-by-token
category: 依賴注入
tags: [di, token, interface]
---

# 對外部邊界用 interface + custom token 注入

> 對外部服務、第三方串接這類邊界，注入 interface 搭配 custom token，而非直接綁死 concrete class，方便替換實作與測試。

## 原因

- TypeScript 的 interface 在執行期會被抹除，無法直接當注入 token，必須搭配 string / Symbol token。
- 依賴 interface 而非 concrete class，能在不改呼叫端的前提下抽換實作（正式版、mock 版、不同 provider）。
- 這是 Dependency Inversion 的落地方式，讓高層邏輯不綁定低層細節。

## ❌ Bad

```ts
@Injectable()
export class NotificationService {
  // 直接注入 concrete class，換成別家簡訊服務就要改這裡
  constructor(private readonly twilio: TwilioSmsService) {}

  notify(phone: string, msg: string) {
    return this.twilio.send(phone, msg);
  }
}
```

綁死 `TwilioSmsService`，要換供應商或在測試替換得改 `NotificationService` 本身。

## ✅ Good

```ts
export const SMS_SENDER = Symbol('SMS_SENDER');

export interface SmsSender {
  send(phone: string, msg: string): Promise<void>;
}

@Injectable()
export class NotificationService {
  constructor(@Inject(SMS_SENDER) private readonly sms: SmsSender) {}

  notify(phone: string, msg: string) {
    return this.sms.send(phone, msg);
  }
}

@Module({
  providers: [{ provide: SMS_SENDER, useClass: TwilioSmsService }],
})
export class NotificationModule {}
```

`NotificationService` 只依賴 `SmsSender` 介面，要換實作只需改 module 的 provider 綁定，呼叫端不動。

## 例外

模組內部、不會被替換的一般 service，直接注入 concrete class 即可，不必為了抽象而抽象。
