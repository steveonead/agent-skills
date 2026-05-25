---
name: vitest-best-practices
description: Vitest 測試與設定最佳實踐規則集。撰寫、審查或重構測試與 vitest.config 時使用，涵蓋 test runner 機制、mock / spy、pool 與 monorepo 設定。前後端皆測（node + jsdom / happy-dom）。不適用於 React 元件測試與 HTTP e2e。
---

# Vitest 4 Best Practices

這份規則集針對 Vitest 4 撰寫，特別強調 v3 → v4 的 breaking changes。Vitest 4 移除了大量 v3 選項（`workspace`、`poolOptions`、`coverage.all`、`environmentMatchGlobs`、`deps.inline` 等），並重寫了 mock / spy 與 pool 機制，但 agent 與 LLM 仍傾向沿用舊寫法。規則集把這類 migration 規則集中在 `migration-` 前綴下，確保產出的測試與設定一律走 v4 API。環境假設為 monorepo、前後端皆測：後端走 `node` environment，前端走 jsdom 或 happy-dom，元件測試同樣跑在 jsdom / happy-dom 下。

## 適用時機

- 撰寫新的 Vitest 測試或 `vitest.config.ts`
- 審查既有測試是否使用 v4 寫法
- 從 Vitest 3 升級到 Vitest 4 的 migration 流程
- AI agent 自動產生測試或設定時對齊 v4 API

## 規則分類

| 分類 | 前綴 | 條數 |
|------|------|------|
| Vitest 4 API 強制（避免 v3 移除的寫法） | `migration-` | 6 |
| Mock 與 Spy | `mocking-` | 7 |
| 設定 | `config-` | 3 |
| Fixture 與測試 Context | `fixtures-` | 2 |
| 非同步斷言 | `async-` | 2 |
| 型別測試 | `types-` | 2 |
| Fake Timer | `timers-` | 1 |
| 環境變數與全域 | `env-` | 1 |
| CLI 執行 | `cli-` | 1 |

## 規則速查

### Vitest 4 API 強制

- `migration-workspace-to-projects` — 多 project 設定用 `projects`，`workspace` 與 `defineWorkspace` 已移除
- `migration-pool-flattened` — `poolOptions` 攤平為頂層 `maxWorkers` / `isolate`，`singleThread` / `singleFork` 改用 `maxWorkers: 1, isolate: false`
- `migration-coverage-options` — `coverage.all` / `extensions` / `ignoreEmptyLines` 已移除，改用 `coverage.include`
- `migration-deps-config-moved` — `deps.inline` / `external` / `fallbackCJS` 移到 `server.deps.*`，`deps.optimizer.web` 改名 `client`
- `migration-match-globs-removed` — `environmentMatchGlobs` / `poolMatchGlobs` 已移除，依檔案套不同環境改用 `projects`
- `migration-test-options-position` — `test` / `describe` 的 options 物件改為第 2 參數，不是第 3

### Mock 與 Spy

- `mocking-vi-not-jest` — mock / spy 一律用 `vi.fn` / `vi.mock` / `vi.spyOn`，不用 `jest.*`，這是 AI 最常見的錯誤
- `mocking-vi-mock-factory` — `vi.mock(import('./mod'), factory)` 寫法、預設匯出處理、共用變數用 `vi.hoisted`
- `mocking-constructor-spies` — spy 建構式的 `mockImplementation` 要用 `function` / `class`，不能用 arrow function
- `mocking-restore-reset-clear` — v4 後 `restoreAllMocks` 只還原 `vi.spyOn`；分清 clear / reset / restore 與 config 的 `restoreMocks`
- `mocking-automock-behavior` — automock getter 回傳 `undefined`、instance method 與 prototype 共享狀態、automock 不可被 restore
- `mocking-import-actual` — 部分 mock 用 `vi.importActual` 或 factory 的 `importOriginal`，不用 Jest 的 `requireActual`
- `mocking-avoid-over-mock` — 只 mock 外部邊界，斷言可觀察結果，別斷言內部呼叫順序與次數

### 設定

- `config-projects` — monorepo 用單一 root config 的 `projects`，各 project 設自己的 `environment`
- `config-test-dir` — 限縮測試目錄用 `test.dir`，不堆疊大量 `exclude`
- `config-coverage-include` — 明確列 `coverage.include`，v4 預設只算載入過的檔案

### Fixture 與測試 Context

- `fixtures-test-extend` — 可重用 setup 用 `test.extend` fixture，取代散落的 `beforeEach` 與共用變數
- `fixtures-scope-file` — 同檔案共用昂貴資源用 `scope: 'file'`

### 非同步斷言

- `async-await-assertions` — `expect.poll` 必須 `await`，否則 auto-retry 失準
- `async-resolves-rejects` — 非同步斷言用 `await expect(...).resolves` / `.rejects`，不手動 try/catch

### 型別測試

- `types-test-api` — 型別測試用 `expectTypeOf` / `assertType`，搭配 `typecheck` 設定
- `types-import-from-vitest` — mock 等型別從 `vitest` import，沒有 `jest` namespace

### Fake Timer

- `timers-fake` — `vi.useFakeTimers` 搭配 `advanceTimersByTime`，`afterEach` 用 `vi.useRealTimers` 還原

### 環境變數與全域

- `env-stub` — 改 env / 全域用 `vi.stubEnv` / `vi.stubGlobal`，`afterEach` 用 `unstubAllEnvs` / `unstubAllGlobals` 還原

### CLI 執行

- `cli-run-not-watch` — agent / CI 跑測試用 `vitest run` 或 `--no-watch`，避免裸 `vitest` 卡在 watch mode

## 使用方式

讀取個別規則檔案以取得詳細說明與範例：

```
references/[類別前綴]-[規則名稱].md
```

每個規則檔案包含：
- 說明此規則重要的原因
- 不建議的寫法（含說明）
- 建議的寫法（含說明）
- 補充說明與參考

## 參考來源

- [Vitest 官方文件](https://vitest.dev/)
- [Vitest 4.0 Migration Guide](https://vitest.dev/guide/migration)
- [Vitest 4.0 is out!（Release Blog）](https://vitest.dev/blog/vitest-4)
