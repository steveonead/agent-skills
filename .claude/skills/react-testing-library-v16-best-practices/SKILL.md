---
name: react-testing-library-v16-best-practices
description: React Testing Library v16 最佳實踐規則集，供撰寫、審查或重構 React 元件測試時參考。明確要求 RTL v16 + React 18/19，跑在 jsdom 或 happy-dom（非 browser mode）的純行為層測試環境。適用於新功能測試、PR self-review、RTL v15 → v16 或 React 18 → 19 migration。不適用於 Vitest browser mode（請改用 vitest-browser-react），或 eslint-plugin-testing-library 已涵蓋的 query / cleanup / await 風格規則。
---

# React Testing Library v16 Best Practices

這份規則集聚焦在 RTL v16 本身的框架機制與 v16 / React 19 的 breaking changes，避免沿用舊版 API 的誤用。環境假設為 jsdom 或 happy-dom 上的純行為層測試（邏輯、hook、component 整合），不涵蓋 browser mode。凡是 `eslint-plugin-testing-library` 已能自動檢查的 query / cleanup / await 風格，這裡一律不重複。

## 適用時機

參考這份規則集的時機：
- 撰寫新的 RTL v16 元件 / hook 測試
- 審查現有測試的品質
- RTL v15 → v16、React 18 → 19 的 migration

## 規則分類

| 分類 | 前綴 |
|------|------|
| 安裝與環境設定 | `setup-` |
| v16 / React 19 API 變更 | `api-` |
| userEvent 與非同步 | `event-` |
| render 進階用法 | `render-` |
| query 用法 | `query-` |

## 規則速查

### 安裝與環境設定

- `setup-peer-dom` — v16 把 `@testing-library/dom` 移為 peer dependency，必須跟 RTL 一起顯式安裝
- `setup-dom-env` — vitest `environment` 設 jsdom 或 happy-dom，搭 `globals: true` 啟用 RTL 自動 cleanup
- `setup-dom-env-limits` — 兩模擬器皆非真實瀏覽器，無 layout / computed style / observer，這類斷言需 stub 或別在此測

### v16 / React 19 API 變更

- `api-act-import` — act 從 `react` import，React 19 已把 act 移出 `react-dom/test-utils`
- `api-render-legacyroot` — `legacyRoot` 在 React 19 會拋出錯誤，不可再用
- `api-render-error-handlers` — `onUncaughtError` 已移除，改用 `onCaughtError` / `onRecoverableError`
- `api-no-test-renderer` — 不用已 deprecated 的 `react-test-renderer` / shallow rendering

### userEvent 與非同步

- `event-setup-before-render` — `userEvent.setup()` 在 render 前建立並複用同一實例
- `event-fake-timers` — 搭配 fake timers 時 setup 要傳 `advanceTimers: vi.advanceTimersByTime`

### render 進階用法

- `render-custom-wrapper` — custom render 集中包 Router / Query / Theme providers
- `render-rerender-props` — 測 prop 更新用回傳的 `rerender`，別重新 render 新實例
- `render-hook` — 測 custom hook 用 `renderHook` + `result.current`，會改 state 的呼叫包在 `act` 裡

### query 用法

- `query-byrole-name` — getByRole 搭配 `{ name }` 精準鎖定（只談 API 用法，不論 query 優先序哲學）

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
