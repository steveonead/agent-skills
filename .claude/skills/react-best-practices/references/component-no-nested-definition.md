---
rule: component-no-nested-definition
category: 元件設計
tags: [component, anti-pattern, identity]
---

# 不在元件內定義子元件

> 禁止在另一個元件的 function body 內定義新的元件。子元件必須宣告在 module scope，再透過 props / children 引入。

## 原因

- 父元件每次 render 都會「重新建立」一個全新的子元件 function reference
- React 看到的是不同 component type → unmount 舊的、mount 新的，子元件 state 完全丟失
- DOM input 失焦、動畫重跑、子層 effect cleanup + 重跑，行為怪異到難以除錯
- 即使有自動化檢查，也只擋得了 function component 形式，arrow function 賦值的巢狀定義仍會漏掉，需人工檢視

## ❌ Bad

```tsx
function ProfilePage({ user }: { user: User }) {
  // 每次 render 都建立新的 UserCard
  function UserCard({ name }: { name: string }) {
    const [expanded, setExpanded] = useState(false);
    return (
      <div onClick={() => setExpanded(!expanded)}>
        {name} {expanded ? '▼' : '▶'}
      </div>
    );
  }

  return (
    <>
      <UserCard name={user.name} />
      <UserCard name={user.partnerName} />
    </>
  );
}
```

每次 `ProfilePage` re-render，`UserCard` 都是新的 component type，內部 `expanded` state 直接歸零。

## ✅ Good

```tsx
// 子元件在 module scope 宣告
function UserCard({ name }: { name: string }) {
  const [expanded, setExpanded] = useState(false);
  return (
    <div onClick={() => setExpanded(!expanded)}>
      {name} {expanded ? '▼' : '▶'}
    </div>
  );
}

function ProfilePage({ user }: { user: User }) {
  return (
    <>
      <UserCard name={user.name} />
      <UserCard name={user.partnerName} />
    </>
  );
}
```

## 例外

- 透過 `children` 傳入的 JSX **元素**不算定義新元件，是合法的（例如 `<List>{items.map(item => <Item key={item.id} />)}</List>`）
- 真的需要把 closure 變數帶進子元件時，把那些變數改成 props 傳進去
