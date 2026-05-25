---
rule: component-hook-return
category: 元件設計
tags: [component, hook, api-design]
---

# Custom Hook 回傳值與設計慣例

> 多值回傳必須用 object，value+setter 才能用 array，且元素數固定為 2。Hook 禁止回傳 JSX。

## 原因

- Object 回傳讓消費者用解構命名，不會因 array 位置混淆（例：`{ data, isLoading, error }`）
- Array 回傳僅適合 value+setter 對（模仿 `useState`），多於兩個元素必混亂
- Hook 回傳 JSX 代表它應該是一個元件，不是 hook

## 回傳形式對照

| 情境 | 回傳形式 | 範例 |
| --- | --- | --- |
| 多個相關值 | Object | `{ data, isLoading, error }` |
| 單一值 + setter | Array（長度 2） | `[value, setValue]` |
| 單一值（唯讀） | 直接回傳 | `return width` |

## ❌ Bad

```tsx
// Hook 回傳 JSX，應改寫為元件
function useUserCard(user: User) {
  return <div className="card">{user.name}</div>;
}

// 只在一處用就抽 hook，屬於過早抽象
function useSubmitHandler() {
  const handleSubmit = () => {
    /* 只用一次 */
  };
  return handleSubmit;
}

// 多值卻用 array，位置容易混淆
function useAuth() {
  return [user, isLoading, error, login, logout];
}
```

## ✅ Good

```tsx
// 多值 — object
function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  // ...
  return { user, isLoading, login, logout };
}

// value + setter — array
function useToggle(initial = false) {
  const [value, setValue] = useState(initial);
  const toggle = () => setValue(previous => !previous);
  return [value, toggle] as const;
}

// 單一唯讀值 — 直接回傳
function useWindowWidth() {
  const [width, setWidth] = useState(window.innerWidth);
  useEffect(() => {
    const handler = () => setWidth(window.innerWidth);
    window.addEventListener('resize', handler);
    return () => window.removeEventListener('resize', handler);
  }, []);
  return width;
}
```
