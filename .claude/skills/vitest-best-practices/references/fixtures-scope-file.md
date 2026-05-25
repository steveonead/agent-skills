---
rule: fixtures-scope-file
category: Fixture 與測試 Context
tags: [fixtures, scope, file, performance]
---

# 同檔共用昂貴資源用 `scope: 'file'`

> 預設 fixture 每個測試都重建一次。若資源建立成本高（資料庫連線、啟動 server、載入設定）且同檔測試可共用，把 fixture 設成 `scope: 'file'`，整個檔案只初始化一次。

## 原因

- 預設 test scope 的 fixture 每個 test 都重跑 setup / teardown，昂貴資源會拖慢整檔
- `scope: 'file'` 讓同檔測試共用同一份資源，檔案結束才清理
- 搭配 `test.extend` 的 suite-level hooks（`test.beforeAll` 等）可在共用資源上做檔案層級準備

## ❌ Bad

```ts
const test = base.extend<{ server: Server }>({
  server: async ({}, use) => {
    const server = await startServer() // 每個 test 都重啟，很慢
    await use(server)
    await server.close()
  },
})
```

## ✅ Good

```ts
const test = base.extend<{ server: Server }>({
  server: [
    async ({}, use) => {
      const server = await startServer()
      await use(server)
      await server.close()
    },
    { scope: 'file' }, // 整個檔案只啟動一次
  ],
})

test('responds to GET', async ({ server }) => {
  expect((await server.request('/health')).status).toBe(200)
})
```

只在資源確實可跨測試共用時才用 `file` scope；若測試之間會互相影響狀態，維持預設的 test scope 較安全。
