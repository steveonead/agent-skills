---
rule: migration-deps-config-moved
category: Vitest 4 API 強制
tags: [migration, deps, server, optimizer, inline]
---

# 依賴處理選項移到 `server.deps`

> Vitest 4 移除頂層的 `deps.external` / `deps.inline` / `deps.fallbackCJS`，改放在 `server.deps.*`。`deps.optimizer.web` 也改名為 `deps.optimizer.client`。

## 原因

- v4 用 Vite 的 Module Runner 取代 `vite-node`，inline / externalize 的設定統一掛在 `server.deps` 下
- `deps.optimizer.web` 的命名對應到 Vite environment，client 環境改稱 `client`，可搭配其他自訂環境名
- 頂層 `deps` 仍保留給 `optimizer`、`interopDefault` 等，但 inline / external 已不在此

## ❌ Bad

```ts
export default defineConfig({
  test: {
    deps: {
      inline: ['some-esm-lib'],
      external: ['legacy-cjs-lib'],
      optimizer: {
        web: { include: ['react'] },
      },
    },
  },
})
```

## ✅ Good

```ts
export default defineConfig({
  test: {
    server: {
      deps: {
        inline: ['some-esm-lib'],
        external: ['legacy-cjs-lib'],
      },
    },
    deps: {
      optimizer: {
        client: { include: ['react'] },
      },
    },
  },
})
```

`inline` / `external` 搬到 `server.deps`，optimizer 的 `web` 改成 `client`。
