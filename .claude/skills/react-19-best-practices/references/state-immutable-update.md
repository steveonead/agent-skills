---
rule: state-immutable-update
category: 狀態管理
tags: [state, immutable, anti-pattern]
---

# 禁止直接 mutate state

> 存在 `useState` / `useReducer` / store 內的 object 或 array 必須當作 read-only。所有更新都要建立新的 reference，禁止用 `.push()`、`obj.x = ...`、`splice` 等 mutating 操作。

## 原因

- React 用 reference 識別 state 是否變化，mutate 同一個 object 時 React 無法察覺，UI 不會更新
- Mutating 操作可能誤動到還在使用舊值的元件，造成跨元件資料污染
- Strict Mode 與 React DevTools 沒有針對 function component mutate 的 lint，agent 經常踩這個坑

## ❌ Bad

```tsx
function TodoList() {
  const [todos, setTodos] = useState<Todo[]>([]);

  function add(todo: Todo) {
    todos.push(todo);       // mutate
    setTodos(todos);        // 同一個 reference，React 不會 re-render
  }

  function toggle(id: string) {
    const target = todos.find(todo => todo.id === id);
    if (target) target.done = !target.done; // mutate
    setTodos(todos);
  }
}
```

```tsx
function Profile() {
  const [user, setUser] = useState({ name: 'Alice', address: { city: 'Taipei' } });

  function moveTo(city: string) {
    user.address.city = city; // mutate 巢狀 object
    setUser(user);
  }
}
```

## ✅ Good

```tsx
function TodoList() {
  const [todos, setTodos] = useState<Todo[]>([]);

  function add(todo: Todo) {
    setTodos(previous => [...previous, todo]);
  }

  function toggle(id: string) {
    setTodos(previous =>
      previous.map(todo => (todo.id === id ? { ...todo, done: !todo.done } : todo)),
    );
  }

  function remove(id: string) {
    setTodos(previous => previous.filter(todo => todo.id !== id));
  }
}
```

```tsx
function Profile() {
  const [user, setUser] = useState({ name: 'Alice', address: { city: 'Taipei' } });

  function moveTo(city: string) {
    setUser(previous => ({
      ...previous,
      address: { ...previous.address, city },
    }));
  }
}
```

## 巢狀過深時用 Immer

State 結構巢狀超過兩層、spread 展開過於繁瑣時，改用 Immer：

```tsx
import { produce } from 'immer';

setUser(produce(draft => {
  draft.address.city = 'Tainan';
  draft.preferences.notifications.email = false;
}));
```

或 Zustand 的 immer middleware 也同樣道理。

## 更新方法對照

| 操作 | ❌ Mutating | ✅ Immutable |
| --- | --- | --- |
| 加入元素 | `arr.push(x)` | `[...arr, x]` |
| 移除元素 | `arr.splice(i, 1)` | `arr.filter((_, index) => index !== i)` |
| 更新元素 | `arr[i].x = v` | `arr.map((item, index) => index === i ? { ...item, x: v } : item)` |
| 更新 object 欄位 | `obj.x = v` | `{ ...obj, x: v }` |
| 排序 | `arr.sort()` | `[...arr].sort()` |
| 反轉 | `arr.reverse()` | `[...arr].reverse()` |
