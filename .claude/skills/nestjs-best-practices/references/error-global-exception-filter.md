---
rule: error-global-exception-filter
category: 錯誤處理
tags: [error, exception-filter, zod]
---

# 用全域 exception filter 統一錯誤格式

> 註冊全域 exception filter 統一錯誤回應結構，並在其中接住 `nestjs-zod` 的 `ZodValidationException`，避免各處錯誤格式不一或外洩內部細節。

## 原因

- 沒有統一 filter，不同例外回傳的 JSON 結構各異，前端難以一致解析。
- 未處理的例外可能把 stack trace、內部訊息漏給 client，造成資訊洩漏。
- 驗證失敗（`ZodValidationException`）的錯誤需要轉成對前端友善的欄位錯誤格式，集中在 filter 處理最一致。

## ❌ Bad

```ts
@Catch()
export class AnyExceptionFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost) {
    const res = host.switchToHttp().getResponse();
    // 直接把 exception 整包丟回去，可能外洩 stack 與內部訊息
    res.status(500).json({ exception });
  }
}
```

把例外整包回傳，內部細節外洩，且所有錯誤都變成 500，狀態碼失真。

## ✅ Good

```ts
import { ZodValidationException } from 'nestjs-zod';

@Catch()
export class GlobalExceptionFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost) {
    const res = host.switchToHttp().getResponse();

    if (exception instanceof ZodValidationException) {
      const zodError = exception.getZodError();
      return res.status(400).json({
        statusCode: 400,
        error: 'ValidationError',
        issues: zodError.issues, // 對前端友善的欄位錯誤
      });
    }

    if (exception instanceof HttpException) {
      const status = exception.getStatus();
      return res.status(status).json({
        statusCode: status,
        error: exception.name,
        message: exception.message,
      });
    }

    // 未預期錯誤：對外只給通用訊息，細節留在 log
    return res.status(500).json({ statusCode: 500, error: 'InternalServerError' });
  }
}

// main.ts
app.useGlobalFilters(new GlobalExceptionFilter());
```

filter 統一回應結構，驗證錯誤轉成欄位 issues，未預期錯誤對外只給通用訊息，細節靠 logger 記錄不外洩。
