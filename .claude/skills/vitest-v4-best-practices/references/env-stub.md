---
rule: env-stub
category: 環境變數與全域
tags: [env, vi.stubEnv, vi.stubGlobal, unstubAllEnvs]
---

# 改 env 與全域用 `vi.stubEnv` / `vi.stubGlobal`

> 測試需要改 `process.env` 或全域物件時，用 `vi.stubEnv()` / `vi.stubGlobal()`，並在 `afterEach` 用 `vi.unstubAllEnvs()` / `vi.unstubAllGlobals()` 還原。直接賦值 `process.env.X = ...` 會殘留到其他測試。

## 原因

- 直接改 `process.env` 或 `globalThis` 是全域副作用，沒還原會污染後續測試
- `stubEnv` / `stubGlobal` 會記錄原值，`unstubAll*` 一次還原，清理可靠
- 可在 config 開 `unstubEnvs: true` / `unstubGlobals: true`，每個測試前自動還原

## ❌ Bad

```ts
test('uses production api', () => {
  process.env.NODE_ENV = 'production' // 殘留到別的測試
  globalThis.fetch = vi.fn()
  expect(getApiBaseUrl()).toBe('https://api.example.com')
})
```

## ✅ Good

```ts
afterEach(() => {
  vi.unstubAllEnvs()
  vi.unstubAllGlobals()
})

test('uses production api', () => {
  vi.stubEnv('NODE_ENV', 'production')
  vi.stubGlobal('fetch', vi.fn())
  expect(getApiBaseUrl()).toBe('https://api.example.com')
})
```

在 config 設 `unstubEnvs: true` 與 `unstubGlobals: true` 後，可省去手寫的 `afterEach` 還原。
