---
rule: validation-strict-schema
category: 驗證（Zod 整合）
tags: [validation, zod, strict, nestjs-zod]
---

# 開啟 strictSchemaDeclaration

> 用 `createZodValidationPipe({ strictSchemaDeclaration: true })`，確保每個請求參數都綁到 Zod DTO 才放行，避免漏掉驗證的入口。

## 原因

- 預設情況下，參數若用原始型別（`string`）或忘了用 Zod DTO，pipe 會靜默放行，留下沒被驗證的入口。
- 開啟 strict 後，遇到沒綁 Zod DTO 的參數會在 runtime 直接拋例外，逼開發者補上 schema，把遺漏的入口變成顯性錯誤。
- 這符合「邊界一次驗證」原則，確保所有外部輸入都先過 schema。

## ❌ Bad

```ts
@Controller('search')
export class SearchController {
  @Get()
  // keyword 用原始 string，沒有 Zod DTO，預設 pipe 靜默放行不驗證
  search(@Query('keyword') keyword: string) {
    return this.searchService.run(keyword);
  }
}
```

`keyword` 沒有經過任何 schema，長度、格式都沒擋，這類漏洞在預設模式下不會被察覺。

## ✅ Good

```ts
import { createZodValidationPipe } from 'nestjs-zod';

const StrictZodValidationPipe = createZodValidationPipe({
  strictSchemaDeclaration: true,
});

@Module({
  providers: [{ provide: APP_PIPE, useClass: StrictZodValidationPipe }],
})
export class AppModule {}

// 參數改用 Zod DTO，否則 strict pipe 會直接報錯
class SearchQueryDto extends createZodDto(
  z.object({ keyword: z.string().min(1).max(100) }),
) {}

@Controller('search')
export class SearchController {
  @Get()
  search(@Query() query: SearchQueryDto) {
    return this.searchService.run(query.keyword);
  }
}
```

strict 模式逼每個入口都用 Zod DTO，沒綁 schema 的參數一被請求打到就會在 runtime 直接報錯，而不是靜默放行。
