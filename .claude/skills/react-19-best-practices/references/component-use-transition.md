---
rule: component-use-transition
category: 元件設計
tags: [component, useTransition, concurrent]
---

# useTransition 處理昂貴的純客戶端運算

> 純客戶端的昂貴同步運算（大量列表 filter、tab 切換造成重 render）必須用 `useTransition`，保留目前 UI 可互動。禁止用於資料 fetch 或路由切換。

## 原因

- 手動管理 `isLoading` state 需要在正確時機執行 set / reset，容易遺漏
- `useTransition` 讓 React 把標記為 transition 的更新放低優先級，UI 保持可互動
- `isPending` 自動回到 false，不需要自己控制

## 在本專案的適用範圍

React 19 的 `useTransition` 技術上支援 async function，包含 fetch 與路由切換都能包進 transition。但**本專案前提**是:

- **資料 fetch**：交給 TanStack Query 的 `isPending` / `isFetching`，不需再用 `useTransition` 包
- **路由切換**:交給 TanStack Router 的 `pendingComponent`

因此 `useTransition` 在本專案只用於「純客戶端昂貴同步運算造成 UI 卡住」的場景。

## ❌ Bad

```tsx
function FilteredList() {
  const [filter, setFilter] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  function handleFilter(value: string) {
    setIsLoading(true);
    setFilter(value);
    // 什麼時候 setIsLoading(false)? 沒人知道
  }

  return (
    <>
      <input onChange={event => handleFilter(event.target.value)} />
      <div style={{ opacity: isLoading ? 0.7 : 1 }}>
        <ExpensiveList filter={filter} />
      </div>
    </>
  );
}
```

## ✅ Good

```tsx
function FilteredList() {
  const [isPending, startTransition] = useTransition();
  const [filter, setFilter] = useState('');

  function handleFilter(value: string) {
    startTransition(() => {
      setFilter(value);
    });
  }

  return (
    <>
      <input onChange={event => handleFilter(event.target.value)} />
      <div style={{ opacity: isPending ? 0.7 : 1 }}>
        <ExpensiveList filter={filter} />
      </div>
    </>
  );
}
```

輸入框立即反映輸入值，重 render 的 `ExpensiveList` 在背景持續計算，`isPending` 期間 UI 仍維持可互動。
