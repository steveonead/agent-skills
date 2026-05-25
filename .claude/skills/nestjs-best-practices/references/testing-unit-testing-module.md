---
rule: testing-unit-testing-module
category: 測試
tags: [testing, unit-test, testing-module]
---

# 單元測 provider 用 Test.createTestingModule

> 單元測試 service 時，用 `Test.createTestingModule` 組一個最小 module，只放被測 provider，用 `overrideProvider().useValue()` 把相依換成 mock，不要啟動整個 app。

## 原因

- 單元測試只該驗被測 service 的邏輯，把相依（repository、外部服務）換成 mock 才能隔離。
- 用 NestJS 的 testing module 取得 provider，能維持與正式環境一致的注入方式，比手動 `new` 接近真實。
- `overrideProvider` 替換的是注入邊界，不需動到正式 module 結構。

> 此處談的是 service 單元測試，不涉及 e2e 層級（啟動完整 app、打 HTTP）的測試骨架與通用 mock 寫法。

## ❌ Bad

```ts
// 手動 new，繞過 DI，且相依沒被隔離
const repo = new UsersRepository(new PrismaService());
const service = new UsersService(repo);

it('throws when user missing', async () => {
  await expect(service.findById('x')).rejects.toThrow(NotFoundException);
});
```

手動 `new` 串接整條依賴鏈，等於連 repository、Prisma 一起測，不是單元測試。

## ✅ Good

```ts
import { Test } from '@nestjs/testing';

describe('UsersService', () => {
  let service: UsersService;
  const repo = { findById: vi.fn() };

  beforeEach(async () => {
    const moduleRef = await Test.createTestingModule({
      providers: [UsersService, UsersRepository],
    })
      .overrideProvider(UsersRepository)
      .useValue(repo) // 把相依換成 mock
      .compile();

    service = moduleRef.get(UsersService);
  });

  it('throws when user missing', async () => {
    repo.findById.mockResolvedValue(null);
    await expect(service.findById('x')).rejects.toThrow(NotFoundException);
  });
});
```

只放被測 service，用 `overrideProvider` 把 repository 換成 mock，隔離出 `UsersService` 自身的邏輯來驗證。
