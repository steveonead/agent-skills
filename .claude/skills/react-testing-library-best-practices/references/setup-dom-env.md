---
rule: setup-dom-env
category: 安裝與環境設定
tags: [setup, vitest, environment, cleanup]
---

# 設定 DOM 環境與自動 cleanup

> vitest 把 `environment` 設成 jsdom 或 happy-dom，並開 `globals: true`，讓 RTL 自動在每個測試後 cleanup。

## 原因

- RTL 需要一個 DOM 環境才能 render，node 預設環境沒有 `document`，直接 render 會失敗。
- RTL 的自動 cleanup 靠 `afterEach` 註冊，只有在 vitest globals 開啟時才會自動掛上；沒開又沒手動 cleanup，元件會殘留並跨測試污染（重複出現、query 撞到多筆）。
- jsdom 與 happy-dom 對 RTL 的 API 行為一致，可任選，happy-dom 較快、jsdom 較完整。但同一專案建議固定其中一個，兩者在少數邊角行為有差，混用容易 flaky。

## ❌ Bad

```ts
// vitest.config.ts — 沒設 environment，globals 也沒開
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {},
})
```

render 會因為沒有 `document` 而失敗，或就算另外給了環境，元件也不會自動 cleanup。

## ✅ Good

```ts
// vitest.config.ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    environment: 'happy-dom', // 或 'jsdom'，擇一固定
    globals: true,            // RTL 才會自動註冊 afterEach(cleanup)
  },
})
```

若不想開 globals，就在 setup file 手動補 cleanup：

```ts
// vitest.setup.ts
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

afterEach(() => {
  cleanup()
})
```

並在 config 設 `setupFiles: ['./vitest.setup.ts']`。注意這是「沒開 globals 時的環境設定」，不是在每個測試裡手動呼叫 cleanup。
