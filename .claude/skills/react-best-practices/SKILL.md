---
name: react-best-practices
description: React 元件與 Hook 最佳實踐規則集。撰寫、審查或重構 React 元件程式碼時使用，涵蓋元件設計、Hook、Effect、效能與安全。針對 Vite + React、搭配 TanStack 的 SPA 環境。不適用於 SSR / RSC、Next.js App Router 等非 Vite SPA 場景。
---

# React 19 Best Practices

針對 Vite + React 19 + TanStack 系列的 SPA 環境，整理出 React 本身的高 ROI 規則。專注於 React 元件設計、Hook 使用、Effect 管理、效能與安全議題。

## 適用時機

參考這份規則集的時機：
- 撰寫新的 React 元件或 Hook
- 審查 PR 中的 React 程式碼品質
- 重構既有的 Class component / React 18 程式碼為 React 19 風格
- 排查效能問題或 re-render 異常

## 規則分類

| 分類 | 前綴 |
|------|------|
| Bundle 拆分與動態載入 | `bundle-` |
| 元件設計 | `component-` |
| Effect 與副作用 | `effect-` |
| 效能 | `performance-` |
| 狀態管理 | `state-` |
| 安全性 | `security-` |
| shadcn/UI 整合 | `shadcn-` |

## 規則速查

### Bundle 拆分與動態載入

- `bundle-conditional-import` — 大型模組與超過 50KB 元件用動態 `import()` / `React.lazy()` 載入
- `bundle-defer-third-party` — 非關鍵第三方 library 用 `React.lazy()` 或動態 `import()` 延後載入

### 元件設計

- `component-variant-over-boolean` — 變體元件取代 boolean prop 堆疊
- `component-compiler-memo` — React Compiler 自動處理 memoization，禁止手寫 `useMemo` / `useCallback` / `React.memo`
- `component-shared-state` — 跨層狀態共享：composition / compound / store，禁止 prop drilling 超過 2 層
- `component-hook-return` — Custom Hook 多值用 object、value+setter 用 array，禁止回傳 JSX
- `component-error-boundary` — Error Boundary 與 Suspense 配對，依業務區塊切，避免 waterfall
- `component-extract-hook` — 資料 fetch、訂閱、複雜運算抽 custom hook，元件保持薄
- `component-no-nested-definition` — 禁止在元件內定義子元件
- `component-use-transition` — `useTransition` 處理昂貴的純客戶端運算

### Effect 與副作用

- `effect-init-module-scope` — App 初始化放 module scope，禁止依賴 `useEffect(fn, [])`
- `effect-event-handler` — 互動邏輯放 event handler，不用 state + effect 模擬事件
- `effect-no-state-sync` — 禁止用 `useEffect` 同步兩個 state，derived state 直接在 render 計算
- `effect-cleanup` — timer、訂閱、event listener、AbortController 必須回傳 cleanup function
- `effect-primitive-deps` — Effect 依賴用 primitive 值而非整個物件

### 效能

- `performance-lazy-init-state` — `useState` 昂貴初始值用 function form
- `performance-stable-key` — 列表 key 禁用 `Math.random()` 或每次 render 變動的值
- `performance-derived-subscription` — 訂閱衍生 boolean 而非連續變動的原始值
- `performance-use-ref-for-mutable` — 不觸發 re-render 的值用 `useRef`

### 狀態管理

- `state-immutable-update` — 禁止直接 mutate state，用 spread / map / filter 或 Immer
- `state-ui-only-store` — Client state store 只放純 UI 狀態
- `state-server-cache` — Server data 交給 server-state cache，禁止存進 client store
- `state-url-search-params` — 可分享狀態放 URL search params

### 安全性

- `security-sanitize-html` — `dangerouslySetInnerHTML` 必須消毒，使用者 URL 必須驗證 scheme

### shadcn/UI 整合

- `shadcn-ui-folder-reserved` — `components/ui/` 只放 shadcn 原始元件
- `shadcn-modify-restrictions` — 限制直接修改 shadcn 原始碼的場景

## 使用方式

讀取個別規則檔案以取得詳細說明與範例：

```
references/<類別前綴>-<規則名稱>.md
```

每個規則檔案包含：
- 說明此規則重要的原因
- `❌ Bad` 反例與 `✅ Good` 正確寫法
- 例外情況（若有白名單）
- 延伸參考連結（若有）
