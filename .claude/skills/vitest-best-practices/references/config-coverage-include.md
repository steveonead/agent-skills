---
rule: config-coverage-include
category: 設定
tags: [config, coverage, include, v8, monorepo]
---

# 明確列出 `coverage.include`

> Vitest 4 的 coverage 預設只計算測試執行期間載入過的檔案。若不設 `coverage.include`，從未被任何測試 import 的檔案不會出現在報告，覆蓋率會被高估。monorepo 要明確列出各 package 的 `src`。

## 原因

- v4 移除 `coverage.all`，預設不再掃描整個專案，沒被載入的檔案直接缺席於報告
- 不設 `include` 時，「完全沒測到」的模組會被當成不存在，而非 0% 覆蓋
- 明確的 `include` 讓覆蓋率反映真實情況，也避免把壓縮檔、設定檔算進去

## ❌ Bad

```ts
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      // 沒設 include：沒被任何測試 import 的檔案不會計入，覆蓋率會被高估
    },
  },
})
```

## ✅ Good

```ts
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      include: ['packages/**/src/**/*.{ts,tsx}'],
      exclude: [
        '**/*.config.*',
        '**/*.d.ts',
        '**/__mocks__/**',
        '**/index.ts', // 純 re-export
      ],
    },
  },
})
```

`include` 命中的檔案即使沒被載入也會以 0% 計入，覆蓋率才不會因「漏寫測試」而被高估。
