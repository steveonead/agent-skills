---
name: zustand-best-practices
description: Zustand 最佳實踐規則集，供撰寫、審查或重構 Zustand store 相關程式碼時參考。明確要求使用 Zustand v5 API，假設環境為純 SPA、無 SSR。適用於新功能開發、PR self-review、Zustand v4 → v5 migration。不適用於 Zustand v3 / v4 專案，或需要 SSR / Next.js App Router 整合的場景。
---

# Zustand Best Practices

Zustand v5 store 的設計與效能規則集，聚焦在 store 結構、selector 用法、middleware 組合、v5 升級雷區與元件層面的常見錯誤，幫助維持 client state 邏輯集中、re-render 可控、行為可預期。

## 適用時機

參考這份規則集的時機：
- 撰寫新的 Zustand store 或 selector hook
- 為 PR 進行 self-review，確認 store / selector / middleware 寫法
- 從 Zustand v4 升級到 v5，檢查破壞性行為

## 規則分類

| 分類 | 前綴 |
|------|------|
| Store 設計 | `store-` |
| 效能 | `perf-` |
| Middleware | `middleware-` |
| v5 升級 | `v5-` |
| 元件慣例 | `component-` |

## 規則速查

### Store 設計

- `store-actions-object` — Action 全部集中在 store 的 `actions` 物件，禁止元件直接呼叫 `setState`
- `store-module-level-actions` — React 元件外（loader、utility）呼叫 action 用 module-level function
- `store-no-fetch-in-actions` 🚨 — Action 只負責 `set()` client state，data fetching 一律交給 TanStack Query
- `store-initial-state-object` — initialState 抽成獨立物件，讓 `reset()` 不需要重複列每個欄位
- `store-one-per-domain` — 一個 store 對應一個 domain，避免單一巨型 store 把不相關的 state 揉在一起
- `store-no-derived-state` — Derived state 用 selector 即時計算，不寫成 store 欄位
- `store-no-direct-mutation` — `set()` 的 updater 不可直接 mutate state，永遠回傳新物件

### 效能

- `perf-selector-with-hooks` 🚨 — 透過 selector + custom hooks 精準取值，禁止 `useStore()` 訂閱整個 store
- `perf-use-shallow-import-path` 🚨 — `useShallow` 必須從 `zustand/react/shallow` import
- `perf-keep-selector-simple` — Selector 內保持單純存取，轉換邏輯放在 custom hook 內
- `perf-multiple-hooks-over-object-selector` — 取多個欄位優先多次呼叫 hook，只有需要單一物件時才用 `useShallow`

### Middleware

- `middleware-devtools-persist-order` 🚨 — `devtools` 包外層、`persist` 包內層，不可顛倒
- `middleware-persist-partialize` — 用 `partialize` 明確列出要持久化的欄位，暫時性 UI state 不得進 storage

### v5 升級

- `v5-no-equality-fn-in-create` 🚨 — `create()` 不再接受第二個 equalityFn 參數，要自訂 equality 改用 `createWithEqualityFn`
- `v5-stable-selector-output` 🚨 — Selector 必須回傳 stable reference，回傳新建立的物件或陣列會導致 infinite loop

### 元件慣例

- `component-no-store-inside-component` — `create()` 只能在 module top-level 呼叫，禁止寫在 React 元件內部

## 使用方式

讀取個別規則檔案以取得詳細說明與範例：

```
references/<類別前綴>-<規則名稱>.md
```

每個規則檔案包含：
- 說明此規則重要的原因
- 不建議的寫法（含說明）
- 建議的寫法（含說明）
- 必要時補充例外情境
