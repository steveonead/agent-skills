---
rule: config-projects
category: 設定
tags: [config, projects, monorepo, environment, node, jsdom, happy-dom]
---

# Monorepo 用單一 root config 的 `projects`

> 前後端混測的 monorepo，用單一 `vitest.config.ts` 的 `test.projects` 列出各 project，每個 project 設自己的 `environment`：後端 `node`、前端 `jsdom` 或 `happy-dom`（元件測試同樣跑在這個 DOM 環境下）。一次指令跑完所有 project。

## 原因

- 環境綁在 project 層級，行為明確且可平行，取代已移除的 `environmentMatchGlobs`
- 共用的 root 設定（alias、coverage、plugin）寫一次，各 project 只覆寫差異
- 後端不必載入 jsdom、前端不必跑 node 專屬設定，互不干擾

## ❌ Bad

```ts
// 把後端與前端勉強放進同一組設定，environment 只能二選一
export default defineConfig({
  test: {
    environment: 'jsdom', // 後端測試其實不需要 DOM
    include: ['packages/**/*.test.ts'],
  },
})
```

## ✅ Good

```ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    projects: [
      {
        test: {
          name: 'server',
          environment: 'node',
          include: ['packages/api/**/*.test.ts'],
        },
      },
      {
        test: {
          name: 'web',
          environment: 'jsdom', // 或 'happy-dom'，純邏輯與元件測試共用
          include: ['packages/web/**/*.test.{ts,tsx}'],
        },
      },
    ],
  },
})
```

前端純邏輯與元件測試共用同一個 DOM project，`environment` 設 `jsdom` 或 `happy-dom` 皆可；happy-dom 較輕量、速度快，jsdom 相容性較完整，依專案需求二選一。
