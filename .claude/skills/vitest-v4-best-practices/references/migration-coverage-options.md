---
rule: migration-coverage-options
category: Vitest 4 API 強制
tags: [migration, coverage, v8, include, deprecated]
---

# Coverage 改用 `include`，移除 `all` 等選項

> Vitest 4 移除了 `coverage.all`、`coverage.extensions`、`coverage.ignoreEmptyLines`、`coverage.experimentalAstAwareRemapping`。報告改成預設只包含執行期間載入的檔案，要納入未覆蓋檔案請改用 `coverage.include`。

## 原因

- v3 的 `all: true` + `include: '**'` 預設會掃描所有檔案，常把壓縮後的 JS 一起算進去，導致報告緩慢甚至卡住
- v4 的 V8 provider 改用 AST-based remapping，`experimentalAstAwareRemapping` 變成預設且唯一方式，舊選項失效
- `ignoreEmptyLines` 移除，沒有 runtime code 的行本來就不再計入

## ❌ Bad

```ts
export default defineConfig({
  test: {
    coverage: {
      all: true,
      extensions: ['js', 'ts'],
      ignoreEmptyLines: true,
    },
  },
})
```

## ✅ Good

```ts
export default defineConfig({
  test: {
    coverage: {
      // 明確指定要納入報告的檔案（含未覆蓋的）
      include: ['packages/**/src/**/*.{js,ts,tsx}'],
      exclude: ['**/*.config.*', '**/__mocks__/**'],
    },
  },
})
```

不設 `include` 時，報告只會涵蓋測試執行中實際載入過的檔案。monorepo 建議明確列出各 package 的 `src`。
