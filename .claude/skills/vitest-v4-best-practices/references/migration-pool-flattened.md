---
rule: migration-pool-flattened
category: Vitest 4 API 強制
tags: [migration, pool, maxWorkers, isolate, poolOptions]
---

# Pool 設定攤平為頂層選項

> Vitest 4 重寫了 pool 機制並移除 `poolOptions`。`maxThreads` / `maxForks` 合併為頂層 `maxWorkers`，`singleThread` / `singleFork` 改用 `maxWorkers: 1, isolate: false`，`minWorkers` 移除，VM 的 `memoryLimit` 改名 `vmMemoryLimit`。

## 原因

- v4 不再依賴 `tinypool`，`poolOptions` 整個結構失效
- thread / fork 的 worker 數量統一由 `maxWorkers` 控制，不用再分兩套
- 環境變數 `VITEST_MAX_THREADS` / `VITEST_MAX_FORKS` 一併改為 `VITEST_MAX_WORKERS`

## ❌ Bad

```ts
export default defineConfig({
  test: {
    poolOptions: {
      forks: {
        execArgv: ['--expose-gc'],
        isolate: false,
        singleFork: true,
      },
      vmThreads: {
        memoryLimit: '300Mb',
      },
    },
  },
})
```

## ✅ Good

```ts
export default defineConfig({
  test: {
    execArgv: ['--expose-gc'],
    isolate: false,
    maxWorkers: 1,
    vmMemoryLimit: '300Mb',
  },
})
```

`singleFork: true` / `singleThread: true` 的等價寫法是 `maxWorkers: 1` 搭配 `isolate: false`。
