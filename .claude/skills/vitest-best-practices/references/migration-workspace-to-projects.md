---
rule: migration-workspace-to-projects
category: Vitest 4 API 強制
tags: [migration, workspace, projects, monorepo, config]
---

# 多 project 設定用 `projects`

> Vitest 4 移除了 `workspace` 設定與 `defineWorkspace`，也不再支援獨立的 `vitest.workspace.ts`。所有多 project 設定改寫進 `vitest.config.ts` 的 `test.projects`。

## 原因

- `workspace` 在 v3.2 已 deprecate，v4 完整移除，沿用會直接拋出錯誤
- `projects` 與 `workspace` 功能相同，但設定集中在單一 config，monorepo 維護更直覺
- `projects` 不再支援「指向另一個檔案匯出陣列」的舊用法，所有 project 就地宣告

## ❌ Bad

```ts
// vitest.workspace.ts
import { defineWorkspace } from 'vitest/config'

export default defineWorkspace([
  './packages/*',
  {
    test: { name: 'unit' },
  },
])
```

`defineWorkspace` 與獨立的 workspace 檔在 v4 已不存在。

## ✅ Good

```ts
// vitest.config.ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    projects: [
      './packages/*',
      {
        test: { name: 'unit' },
      },
    ],
  },
})
```

把 workspace 檔的內容直接搬進 `test.projects`，刪掉 `vitest.workspace.ts`。
