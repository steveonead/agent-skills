---
rule: performance-stable-key
category: 效能
tags: [performance, key, list, anti-pattern]
---

# 列表 key 禁用 Math.random() 或每次 render 變動的值

> 列表 `key` 必須是穩定的識別值（資料庫 ID、唯一業務 key）。禁止使用 `Math.random()`、`Date.now()`、或任何在 render 中產生的新值。

## 原因

- `react/jsx-key` 與 `react/no-array-index-key` 已經 lint 大部分情況，但 `Math.random()` 等動態值 lint 抓不到
- `key` 是 React 用來追蹤列表項目身份的依據，每次 render 都不同 = 強制 unmount + remount 所有項目
- 結果是：input 失焦、CSS 動畫重跑、子層 state 全丟、效能嚴重下降

## ❌ Bad

```tsx
// 每次 render 都產生新 key，等於每次都 remount
{users.map(user => <li key={Math.random()}>{user.name}</li>)}

// Date.now() 也是同類問題
{messages.map(message => <Message key={Date.now()} {...message} />)}

// crypto.randomUUID() 在 render 中呼叫也一樣
{items.map(item => <Item key={crypto.randomUUID()} {...item} />)}
```

## ✅ Good

```tsx
// 用穩定 ID
{users.map(user => <li key={user.id}>{user.name}</li>)}

// 沒 ID 時，在資料進入 state 前就先補 UUID，而不是在 render 算
const [items, setItems] = useState(() =>
  rawItems.map(item => ({ ...item, _id: crypto.randomUUID() })),
);

{items.map(item => <Item key={item._id} {...item} />)}
```

## 例外:何時可以用 index

- **靜態列表**:不會新增、刪除、排序
- **無內部 state**:沒有 input、checkbox、動畫
- **無需追蹤項目進出**:不需要 transition / animation

```tsx
const menuItems = ['Home', 'About', 'Contact'];
{menuItems.map((item, index) => <a key={index}>{item}</a>)}
```

## Reference

- React 官方:[Rendering Lists — Rules of keys](https://react.dev/learn/rendering-lists#rules-of-keys)
