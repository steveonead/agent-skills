---
rule: bundle-defer-third-party
category: Bundle 拆分與動態載入
tags: [bundle, third-party, lazy, analytics]
---

# 延後載入非關鍵第三方 library

> 不影響首屏互動的第三方 library 必須延後載入。元件型套件（如 `<Analytics />`）用 `React.lazy()` + `<Suspense>`，init 型 SDK（PostHog、Mixpanel、Hotjar）用原生 `import()` 在 idle 或 effect 時機載入。

## 原因

- Analytics、heatmap、A/B testing 等套件不應阻塞首屏 render
- `React.lazy()` 僅接受 React 元件（resolve 出 `default`），對 init 型 SDK 不可用，會在 runtime 拋出錯誤
- 兩種模式都能讓套件從 initial bundle 移出

## ❌ Bad

```tsx
// 全部靜態 import，一律打包進 initial bundle
import { Analytics } from '@vercel/analytics/react';
import posthog from 'posthog-js';

posthog.init('phc_xxx', { api_host: 'https://app.posthog.com' });

function App() {
  return (
    <>
      <MainContent />
      <Analytics />
    </>
  );
}
```

```tsx
// 以 React.lazy 包非元件型 library，runtime 將拋出錯誤
const posthog = lazy(() => import('posthog-js'));
```

## ✅ Good

```tsx
import { lazy, Suspense } from 'react';

const Analytics = lazy(() =>
  import('@vercel/analytics/react').then(module => ({
    default: module.Analytics,
  })),
);

function App() {
  return (
    <>
      <MainContent />
      <Suspense fallback={null}>
        <Analytics />
      </Suspense>
    </>
  );
}
```

```tsx
// PostHog 為 init 型 SDK,在 effect 中動態載入
function PostHogProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    const init = async () => {
      const { default: posthog } = await import('posthog-js');
      posthog.init('phc_xxx', { api_host: 'https://app.posthog.com' });
    };
    void init();
  }, []);

  return <>{children}</>;
}
```

## 例外：必須早期載入的 SDK

以下 library **不該延後**，要在 app 啟動最早期同步載入：

- **Error tracking**（Sentry、Bugsnag）：延後會漏抓 bootstrap 期間的錯誤
- **依賴 auto-instrumentation 的 RUM**（Datadog RUM、New Relic Browser）：需要早期 hook 住 resource timing
- **影響首屏 render 的 critical feature flag**：晚解析會閃畫面

這類套件應放 entry file 最前面，與本規則無關。
