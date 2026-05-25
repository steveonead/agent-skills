---
rule: setup-import-syntax
category: 測試骨架
tags: [setup, typescript, import, esModuleInterop]
---

# 依 esModuleInterop 決定 import 寫法

> supertest 用 CommonJS default export，TypeScript 的 import 寫法必須對齊 `esModuleInterop` 設定，`import { request }` 永遠是錯的。

## 原因

- supertest 沒有 named export `request`，所以 `import { request } from 'supertest'` 在執行期會拿到 undefined 或直接報錯。
- 開了 `esModuleInterop: true`（NestJS CLI 預設）時，用 `import request from 'supertest'` 的 default import 最自然。
- 關閉 `esModuleInterop` 時，要用 `import * as request from 'supertest'` 的 namespace import，否則 TypeScript 會抱怨 `typeof supertest` 不可呼叫。

## ❌ Bad

```ts
import { request } from 'supertest';
// SyntaxError: The requested module 'supertest' does not provide an export named 'request'
```

把 supertest 當成有 named export 來 import，是最常見也最致命的寫法，整個測試檔直接跑不起來。

## ✅ Good

```ts
// tsconfig 開了 esModuleInterop（NestJS 預設）
import request from 'supertest';

// tsconfig 關閉 esModuleInterop 時改用
// import * as request from 'supertest';

it('GET /cats', async () => {
  await request(app.getHttpServer()).get('/cats').expect(200);
});
```

先確認專案 tsconfig 的 `esModuleInterop`，再選對應的 import 形式。NestJS CLI 產生的專案預設開啟，因此 default import 是大多數情況的答案。

## 補充

- 這條只關係 import 形式本身，不重複 ESLint 的 import 排序或風格檢查。
- 取得 server 的部分見 `setup-get-http-server`。
