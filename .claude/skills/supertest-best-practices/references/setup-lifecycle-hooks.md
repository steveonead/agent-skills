---
rule: setup-lifecycle-hooks
category: 測試骨架
tags: [setup, vitest, lifecycle, beforeAll, afterAll]
---

# 在 beforeAll 建立 app、afterAll 收尾

> 用 Vitest 的 `beforeAll` 建立 testing module 並 `app.init()`，在 `afterAll` 關閉，整個 describe 共用一個 app instance。

## 原因

- `Test.createTestingModule().compile()` 與 `app.init()` 成本不低，放在 `beforeEach` 會讓每個 test 重建一次，測試明顯變慢。
- 多數 e2e test 之間不需要重啟整個 app，只需要清資料，所以 app 建立放 `beforeAll`、資料清理放 `beforeEach` / `afterEach` 是合理的分層。
- `afterAll` 負責關閉 app，是避免 process 卡住的關鍵，不能省略。

## ❌ Bad

```ts
import { beforeEach, afterEach } from 'vitest';

describe('Cats (e2e)', () => {
  let app: INestApplication;

  beforeEach(async () => {
    const moduleRef = await Test.createTestingModule({ imports: [AppModule] }).compile();
    app = moduleRef.createNestApplication();
    await app.init(); // 每個 test 都重建整個 app，慢且浪費
  });

  afterEach(async () => {
    await app.close();
  });
});
```

把整個 app 的建立塞進 `beforeEach`，每個 test 都付一次完整啟動成本，測試套件會越長越慢。

## ✅ Good

```ts
import { describe, it, beforeAll, afterAll } from 'vitest';
import { Test } from '@nestjs/testing';
import type { INestApplication } from '@nestjs/common';

describe('Cats (e2e)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleRef = await Test.createTestingModule({ imports: [AppModule] }).compile();
    app = moduleRef.createNestApplication();
    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });
});
```

app 建立一次、整個 describe 共用，收尾交給 `afterAll`。需要逐 test 隔離的是資料狀態，那屬於 `beforeEach`，不是整個 app。

## 補充

- 建立邏輯通常會抽成 factory，見 `setup-test-factory`。
- `afterAll` 為何不可省，見 `cleanup-close-app`。
- 資料層的逐 test 隔離見 `isolation-test-db`。
