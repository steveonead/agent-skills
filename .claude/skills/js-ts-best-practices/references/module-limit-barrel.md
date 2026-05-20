---
rule: module-limit-barrel
category: module
tags: [module, barrel, re-export, tree-shaking]
---

# 限制 barrel export，禁 `export *`

> 預設不建立 `index.ts` barrel 檔案，`export *` 在任何場景都禁止。

## 原因

- `export *` 讓 bundler 無法判斷哪些匯出實際被用，破壞 tree-shaking
- 內部資料夾的 barrel 容易造成循環引用，runtime 出現 `undefined`
- IDE 需要解析整個 barrel 才能補全，型別檢查與自動匯入會變慢
- 團隊混用 barrel 路徑與直接路徑會造成同一模組多種匯入方式

## ❌ Bad

```ts
// 任何場景都禁止 export *
// services/index.ts
export * from './user.service';
export * from './auth.service';

// 非模組邊界的 barrel
// utils/index.ts
export { formatDate } from './date';
export { formatCurrency } from './currency';

// components 資料夾的 barrel
// components/index.ts
export { Button } from './Button';
export { Input } from './Input';
```

`utils/index.ts` 不是模組邊界，建 barrel 只是讓 import 路徑短一點點，卻引入循環引用與 bundle 膨脹風險。

## ✅ Good

```ts
// 直接從原始模組匯入
import { UserService } from '@/services/user.service';
import { formatDate } from '@/utils/date';
import { Button } from '@/components/Button';

// 白名單場景：從模組邊界的公開 API 匯入
import { AuthGuard, useAuth } from '@/features/auth';
import { ThemeProvider } from '@/libs/design-system';
```

一律走完整路徑，路徑變長但避免所有 barrel 帶來的問題。
