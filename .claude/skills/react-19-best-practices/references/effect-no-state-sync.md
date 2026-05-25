---
rule: effect-no-state-sync
category: Effect 與副作用
tags: [effect, derived-state, anti-pattern]
---

# 禁止用 useEffect 同步兩個 state

> 禁止寫 `useEffect(() => setB(transform(a)), [a])` 這類同步 state 的程式碼。Derived state 必須直接在 render 中計算，或在 setter 中與來源 state 一併處理。

## 原因

- `useEffect` 是給 side effect（DOM 操作、訂閱外部系統）的，不是 state 同步工具
- 用 effect 同步 state 會多一個 render cycle，UI 先顯示舊值再閃成新值
- Derived state 直接在 render 算，沒有額外 state、沒有額外 effect

## ❌ Bad

```tsx
function UserList({ users }: { users: User[] }) {
  const [filter, setFilter] = useState('');
  const [filteredUsers, setFilteredUsers] = useState(users);

  // 用 effect 同步 — 多一次 re-render，多一個 state 要管
  useEffect(() => {
    setFilteredUsers(
      users.filter(user => user.name.toLowerCase().includes(filter.toLowerCase())),
    );
  }, [users, filter]);

  return (
    <>
      <input value={filter} onChange={event => setFilter(event.target.value)} />
      <ul>{filteredUsers.map(user => <li key={user.id}>{user.name}</li>)}</ul>
    </>
  );
}
```

## ✅ Good

```tsx
function UserList({ users }: { users: User[] }) {
  const [filter, setFilter] = useState('');

  // 衍生值直接在 render 算，不需要額外 state
  const filteredUsers = users.filter(user =>
    user.name.toLowerCase().includes(filter.toLowerCase()),
  );

  return (
    <>
      <input value={filter} onChange={event => setFilter(event.target.value)} />
      <ul>{filteredUsers.map(user => <li key={user.id}>{user.name}</li>)}</ul>
    </>
  );
}
```

## 判斷準則

問自己：「這個 state 真的能從現有 state / props 算出來嗎？」

- 能算出來 → 移除這個 state，改成 render 中的 const
- 需要在 prop 變動時「重置」內部 state → 改用 `key` prop 觸發 remount
- 真的需要 cache 計算結果 → 直接在 render 算就好，React Compiler 會處理
