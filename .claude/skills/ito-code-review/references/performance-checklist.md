# 效能審查清單

針對 code review 的效能審查速查表，搭配 `ito-code-review` skill 使用。

## 目錄

- [Core Web Vitals 目標值](#core-web-vitals-目標值)
- [前端清單](#前端清單)
- [後端清單](#後端清單)

## Core Web Vitals 目標值

| 指標 | 良好 | 待改善 | 差 |
|------|------|--------|-----|
| LCP（Largest Contentful Paint） | ≤ 2.5s | ≤ 4.0s | > 4.0s |
| INP（Interaction to Next Paint） | ≤ 200ms | ≤ 500ms | > 500ms |
| CLS（Cumulative Layout Shift） | ≤ 0.1 | ≤ 0.25 | > 0.25 |

## 前端清單

### 圖片

- [ ] 使用現代格式（WebP、AVIF）
- [ ] 有 `srcset` 和 `sizes` 做響應式尺寸
- [ ] `<img>` 和 `<source>` 明確指定 `width` 和 `height`，防止 CLS
- [ ] 非首屏圖片加 `loading="lazy"` 和 `decoding="async"`
- [ ] Hero 或 LCP 圖片加 `fetchpriority="high"`，不加 lazy loading

### JavaScript

- [ ] 初始 bundle 在 200KB gzip 以內
- [ ] 路由和重型功能用動態 `import()` 做 code splitting
- [ ] Tree shaking 有效：確認套件有提供 ESM 並標記 `sideEffects: false`
- [ ] `<head>` 裡沒有阻塞渲染的 JavaScript（改用 `defer` 或 `async`）
- [ ] 耗時運算考慮移到 Web Worker
- [ ] Long task（> 50ms）有切割，避免佔住 main thread，是改善 INP 最直接的手段
- [ ] 長迴圈內使用 `yieldToMain` pattern，讓 input 事件有機會在每個區塊之間執行
- [ ] 有用到現代排程 API：`scheduler.yield()`（優先）、`scheduler.postTask()` 含優先權設定、`isInputPending()` 按需讓步
- [ ] `requestIdleCallback` 用於可延後的非緊急工作（如 analytics flush、prefetch、warmup）
- [ ] 非核心工作從 event handler 移出（例如 analytics、logging），不佔用回應時間
- [ ] 第三方 script 用 `async` 或 `defer` 載入，有審查體積，重型嵌入元件（聊天 widget、影片）用 facade 延遲載入

### CSS

- [ ] Critical CSS 有 inline 或 preload
- [ ] 非核心樣式不阻塞渲染
- [ ] CSS-in-JS 在 production 用靜態提取，不留 runtime 計算成本

### 字型

- [ ] 字型家族限 2-3 種，每種字重限 2-3 個（每多一個字重就多一個 request）
- [ ] 只用 WOFF2（最小、全瀏覽器支援，不需要 WOFF/TTF/EOT）
- [ ] 盡量自行 host，避免第三方 font CDN 的額外 DNS、TCP、TLS 延遲
- [ ] LCP 相關字型加 preload：`<link rel="preload" as="font" type="font/woff2" crossorigin>`
- [ ] 用 `font-display: swap`（非核心字型用 `optional`），避免 FOIT 阻塞渲染
- [ ] 用 `unicode-range` 只載入當頁需要的字元子集
- [ ] 需要多個字重或樣式時，考慮用 variable font（一個檔案取代多個）
- [ ] 用 `size-adjust`、`ascent-override`、`descent-override` 調整 fallback 字型指標，減少字型切換時的 CLS
- [ ] 考慮用系統字型堆疊取代自訂字型

### 網路

- [ ] 靜態資源有長效 `max-age` 搭配 content hash
- [ ] API 回應在適當情況下有 `Cache-Control`
- [ ] 啟用 HTTP/2 或 HTTP/3
- [ ] 已知來源加 `<link rel="preconnect">` 預先建立連線
- [ ] 關鍵非圖片資源也有設 `fetchpriority`（不只 `<img>`）
- [ ] 沒有多餘的 redirect

### 渲染

- [ ] 沒有 layout thrashing（強制同步重排）
- [ ] 動畫用 `transform` 和 `opacity`（GPU 加速）
- [ ] 長列表有做虛擬化（virtualization）
- [ ] 沒有不必要的整頁重新渲染
- [ ] 畫面外區塊用 `content-visibility: auto` 搭配 `contain-intrinsic-size`，跳過不可見區域的 layout 和 paint
- [ ] 沒有 `unload` event handler，HTML response 沒有 `Cache-Control: no-store`，確保 bfcache 可用

## 後端清單

### 資料庫

- [ ] 沒有 N+1 查詢（改用 eager loading 或 join）
- [ ] 查詢有適當索引
- [ ] 列表 endpoint 有分頁，不全撈（不能 `SELECT * FROM table`）
- [ ] Connection pooling 設定正確
- [ ] Slow query logging 有開

### API

- [ ] 回應時間 < 200ms（p95）
- [ ] request handler 裡沒有同步的重型運算
- [ ] 批次操作取代迴圈逐筆呼叫
- [ ] 回應有壓縮（gzip 或 brotli）
- [ ] 有適當快取策略（in-memory、Redis、CDN）

### 基礎設施

- [ ] 有 health check endpoint 供 load balancer 使用
