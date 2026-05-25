---
rule: testing-vitest-swc-decorators
category: 測試
tags: [testing, vitest, swc, decorators]
---

# Vitest 跑 NestJS 需處理 decorator metadata

> 用 Vitest 測 NestJS 時，要透過 `unplugin-swc` 編譯並確保載入 `reflect-metadata`，否則 DI 需要的 `emitDecoratorMetadata` 型別資訊會缺失，注入直接失敗。

## 原因

- NestJS 的 DI 靠 `emitDecoratorMetadata` 產生的型別 metadata 解析 constructor 參數，esbuild（Vitest 預設）不會輸出這份 metadata。
- 少了 metadata，`Test.createTestingModule` 在解析依賴時會拿不到型別，注入失敗或拿到 `undefined`。
- 用 `unplugin-swc` 走 SWC 編譯並開啟 decorator 支援，配合載入 `reflect-metadata`，才能讓 DI 在測試環境正常運作。

> 此處只談 NestJS decorator 在測試環境的接點，不涉及 mock 機制與其他測試設定。

## ❌ Bad

```ts
// vitest.config.ts：沒有處理 decorator metadata
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: { globals: true },
});
// 結果：Test.createTestingModule 解析依賴時拿不到型別，注入報錯
```

esbuild 不輸出 decorator metadata，NestJS DI 在測試中無法解析 constructor 參數。

## ✅ Good

```ts
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import swc from 'unplugin-swc';

export default defineConfig({
  plugins: [
    swc.vite({
      jsc: {
        transform: { legacyDecorator: true, decoratorMetadata: true },
      },
    }),
  ],
  test: {
    globals: true,
    setupFiles: ['reflect-metadata'], // 確保 metadata API 可用
  },
});
```

用 `unplugin-swc` 編譯並開啟 `decoratorMetadata`，搭配 `reflect-metadata`，DI 在測試環境就能正確解析依賴。
