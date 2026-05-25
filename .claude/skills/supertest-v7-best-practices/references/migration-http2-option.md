---
rule: migration-http2-option
category: 版本與遷移
tags: [migration, http2, options]
---

# 需要測 HTTP/2 時用初始化 option 開啟

> v7 新增 HTTP/2 支援，透過 `request(app, { http2: true })` 或 `request.agent(app, { http2: true })` 開啟，不需要自己架 http2 server。

## 原因

- HTTP/2 是 v7 才加入的能力，做法是在 `request` 的第二個參數傳入 options 物件，supertest 內部會改用 `http2.createServer` 並處理對應的 lifecycle。
- 不開這個 option 時，supertest 走的是 HTTP/1.1，測不到 HTTP/2 專屬行為（例如 server push、header 壓縮相關路徑）。
- 多數 NestJS e2e 測試不需要 HTTP/2，只有當 production 確實跑 HTTP/2 且要驗證對應行為時才需要。

## ❌ Bad

```ts
// 想測 HTTP/2，卻自己手動架一套 http2 server，繞過 supertest 的封裝
import http2 from 'node:http2';

const server = http2.createServer(/* ... */);
// 自行管理 listen / close，重複造輪子又容易漏關
```

繞過 supertest 自己處理 http2 server，等於放棄它幫你管的 lifecycle，徒增出錯與資源外洩的風險。

## ✅ Good

```ts
import request from 'supertest';

it('支援 HTTP/2 請求', async () => {
  await request(app.getHttpServer(), { http2: true })
    .get('/cats')
    .expect(200);
});
```

用 option 開啟，把 http2 server 的建立與關閉交給 supertest，測試碼維持和 HTTP/1.1 一致的寫法。

## 補充

- 一般 e2e 測試維持預設（不傳 http2 option）即可，這條只在確有 HTTP/2 驗證需求時適用。
