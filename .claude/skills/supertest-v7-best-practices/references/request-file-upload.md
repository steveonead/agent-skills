---
rule: request-file-upload
category: 請求撰寫
tags: [request, upload, multipart, attach, field, formidable]
---

# 檔案上傳用 .field() 搭 .attach()

> multipart / form-data 上傳用 `.attach()` 掛檔案、`.field()` 帶表單欄位，不要自己組 multipart body。升到 supertest v7（superagent v10）後上傳行為有變，要重跑驗證。

## 原因

- `.attach(field, path)` 與 `.field(name, value)` 由 superagent 處理 multipart 編碼與 boundary，自己手動拼 body 容易格式錯、又難維護。
- superagent v10 把底層 formidable 升到 v3，multipart 的解析與回應處理改變，v6 時代能過的上傳測試升級後可能卡住或行為不同。
- 不要混用：同一個請求要嘛全用 `.attach()` / `.field()`，要嘛用 `.send()` 送 JSON，把 multipart 和 `.send()` 混在一起會讓 content-type 衝突。

## ❌ Bad

```ts
it('上傳頭像', async () => {
  // 手動組 multipart body，boundary 與編碼自己拼，極易出錯
  await request(app.getHttpServer())
    .post('/avatar')
    .set('Content-Type', 'multipart/form-data; boundary=----x')
    .send('------x\r\nContent-Disposition: form-data; name="file"...')
    .expect(201);
});
```

手刻 multipart payload，boundary 和編碼稍有差錯就整包失敗，維護成本也高。

## ✅ Good

```ts
it('上傳頭像', async () => {
  await request(app.getHttpServer())
    .post('/avatar')
    .field('name', 'my avatar')
    .attach('file', 'test/fixtures/avatar.jpg')
    .expect(201);
});
```

把 multipart 編碼交給 supertest，欄位用 `.field()`、檔案用 `.attach()`，請求清楚也不會編碼出錯。

## 補充

- `.attach()` 第二參數可傳檔案路徑，也可傳 Buffer 並用第三參數指定檔名與 contentType。
- 升級後上傳測試務必重跑，背景見 `migration-superagent-bump`。
- 上傳測試若在 CI 偶發卡住，先確認版本符合 `migration-pin-safe-version`（v7.1.x 修過 multipart 卡住問題）。
