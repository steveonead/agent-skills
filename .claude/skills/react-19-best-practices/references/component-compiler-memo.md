---
rule: component-compiler-memo
category: 元件設計
tags: [component, performance, react-compiler, memoization]
---

# React Compiler 處理 memoization，禁止手寫 memo

> React 19 啟用 React Compiler 後，禁止手動使用 `useMemo`、`useCallback`、`React.memo`。遇到效能問題的處理順序：重構 composition → React Profiler 定位 → 真的找不到方法時才考慮手動 memo。

## 原因

- React Compiler 會自動穩定 inline object / array / callback，手寫 memo 變多餘
- 手寫的 memo 依賴常常列錯，反而失效或導致 stale closure
- 多數「re-render 太多」的真正原因是 composition 不良，把狀態放錯位置，而非缺少 memo

## ❌ Bad

```tsx
// React Compiler 已自動處理，這些都不需要
function UserCard({ user }: { user: User }) {
  const fullName = useMemo(
    () => `${user.firstName} ${user.lastName}`,
    [user.firstName, user.lastName],
  );

  const handleClick = useCallback(() => {
    console.log(user.id);
  }, [user.id]);

  return <Card onClick={handleClick}>{fullName}</Card>;
}

const MemoCard = React.memo(UserCard);
```

## ✅ Good

```tsx
function UserCard({ user }: { user: User }) {
  const fullName = `${user.firstName} ${user.lastName}`;
  const handleClick = () => console.log(user.id);

  return <Card onClick={handleClick}>{fullName}</Card>;
}
```

## 效能問題的處理順序

1. **重構 composition**：把 state 往下推（抽出 stateful child），或改用 children 傳入避免父層重 render 波及深層子樹
2. **用 React Profiler 量測**：確認到底是哪個元件、哪次 render 慢
3. **最後手段**：Profiler 明確指出某個 inline object 造成昂貴子樹 re-render 時，才考慮手動 memo，並在 commit message 註明原因

## 例外

- 與外部系統互動需要 referential equality 時（例如 Map / Set 當 dependency、IntersectionObserver 的 callback），手寫 memo 是必要的
- 三方 library 強制要求穩定 callback 識別（少數 hook、第三方 useImperativeHandle）時可保留 `useCallback`
