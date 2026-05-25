---
rule: config-test-dir
category: 設定
tags: [config, test.dir, exclude, include, performance]
---

# 限縮測試範圍用 `test.dir` 或 `include`

> Vitest 4 簡化了預設 `exclude`，現在只排除 `node_modules` 與 `.git`。不要靠堆疊一長串 `exclude` 把測試擋在某些資料夾外，改用 `test.dir` 指定測試根目錄，或用精確的 `include` glob，效能更好也更直觀。

## 原因

- v4 不再預設排除 `dist`、`cypress`、各種 config 檔，沿用舊做法靠 exclude 會越列越長
- `test.dir` 直接限定掃描範圍，比逐一排除更快、語意更清楚
- `include` 用精確 glob 命中測試檔，避免掃到無關目錄

## ❌ Bad

```ts
export default defineConfig({
  test: {
    exclude: [
      '**/node_modules/**',
      '**/dist/**',
      '**/cypress/**',
      '**/.{idea,git,cache,output,temp}/**',
      '**/build/**',
      // ...持續增長
    ],
  },
})
```

## ✅ Good

```ts
export default defineConfig({
  test: {
    // 直接限定測試根目錄
    dir: './src',
    // 或用精確 include 命中測試檔
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
  },
})
```

確實需要還原 v3 的預設排除清單時，用 `configDefaults.exclude` 展開再補上自訂項目，而不是手寫全部。
