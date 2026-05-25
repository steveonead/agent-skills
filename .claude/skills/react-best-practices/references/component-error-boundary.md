---
rule: component-error-boundary
category: 元件設計
tags: [component, error-boundary, suspense, resilience]
---

# Error Boundary 與 Suspense 配對，依業務區塊切

> Error Boundary 與 Suspense 都該按業務畫面決定邊界位置，不是「每個元件都包」。fallback 出現的位置要符合使用者當下的工作流，並與 Error Boundary 配對處理錯誤，避免 waterfall。

## 原因

- React 預設會在 render 錯誤時移除 UI，Error Boundary 可改顯示降級畫面
- 邊界粒度是產品決策：取決於錯誤發生時使用者應該在哪裡看到錯誤或 loading
- Suspense 過粗會等待過久，過細則同時出現多個 spinner，造成畫面閃爍
- Suspense 必須與 Error Boundary 一起放，否則 rejected promise 將使整棵 React 子樹卸載

## ❌ Bad

```tsx
// 邊界太粗：整頁發生錯誤只能顯示 generic 訊息
function App() {
  return (
    <ErrorBoundary fallback={<div>Something went wrong</div>}>
      <Router />
    </ErrorBoundary>
  );
}

// 邊界太細：小元件各自包，fallback 無業務語意
<ErrorBoundary fallback={<span>錯誤</span>}>
  <Avatar user={user} />
</ErrorBoundary>;

// Waterfall — 子元件的 fetch 依賴父元件 fetch 結果，串行進行
function Profile({ userId }: { userId: string }) {
  const { data: user } = useSuspenseQuery(userQuery(userId));
  // user.id 拿到才開始抓 posts → 兩段串行
  return (
    <>
      <UserHeader user={user} />
      <UserPosts userId={user.id} />
    </>
  );
}

// 期待 Error Boundary 接住 event handler 的錯誤 — 接不到
function SubmitButton() {
  const handleClick = async () => {
    await submitOrder(); // 拋錯不會被 boundary 接住
  };
  return <button onClick={handleClick}>送出</button>;
}
```

## ✅ Good

```tsx
import { Suspense } from 'react';
import { ErrorBoundary, type FallbackProps } from 'react-error-boundary';
import * as Sentry from '@sentry/react';

// 邊界依業務區塊切，Error Boundary 包 Suspense
function InboxRoute() {
  return (
    <ErrorBoundary
      FallbackComponent={InboxErrorFallback}
      onError={(error, info) => Sentry.captureException(error, { extra: info })}
    >
      <InboxLayout>
        <ErrorBoundary FallbackComponent={ConversationListErrorFallback}>
          <Suspense fallback={<ConversationListSkeleton />}>
            <ConversationList />
          </Suspense>
        </ErrorBoundary>

        <ErrorBoundary FallbackComponent={ThreadErrorFallback}>
          <Suspense fallback={<ThreadSkeleton />}>
            <MessageThread />
          </Suspense>
        </ErrorBoundary>
      </InboxLayout>
    </ErrorBoundary>
  );
}

function ThreadErrorFallback({ resetErrorBoundary }: FallbackProps) {
  return (
    <div className="rounded border p-4">
      <p>無法載入這段對話</p>
      <button onClick={resetErrorBoundary}>重試</button>
    </div>
  );
}

// event handler 內的錯誤自己處理
function SubmitButton() {
  const handleClick = async () => {
    try {
      await submitOrder();
    } catch (error) {
      Sentry.captureException(error);
      toast.error('送出失敗，請稍後再試');
    }
  };
  return <button onClick={handleClick}>送出</button>;
}
```

## Suspense 邊界放置與避免 waterfall

- **多個 Suspense 邊界並列**比一個大邊界好:獨立區塊可以各自填入，不會被慢的拖到
- **避免「父層 fetch → 子層才接著 fetch」的串行**:父層用 `useSuspenseQueries` 一次發起所有需要的請求

```tsx
// 避免 waterfall — 在父層並行觸發
function Profile({ userId }: { userId: string }) {
  const [{ data: user }, { data: posts }] = useSuspenseQueries({
    queries: [userQuery(userId), userPostsQuery(userId)],
  });
  return (
    <>
      <UserHeader user={user} />
      <UserPosts posts={posts} />
    </>
  );
}
```

```tsx
// 並列邊界，各自獨立載入
<Suspense fallback={<HeaderSkeleton />}><Header /></Suspense>
<Suspense fallback={<MainSkeleton />}><Main /></Suspense>
<Suspense fallback={<SidebarSkeleton />}><Sidebar /></Suspense>
```

## Reference

- [React Component docs — Catching rendering errors with an Error Boundary](https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary)
