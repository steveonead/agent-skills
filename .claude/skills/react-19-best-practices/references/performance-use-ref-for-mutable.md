---
rule: performance-use-ref-for-mutable
category: 效能
tags: [performance, useRef, re-render]
---

# 不觸發 re-render 的值用 useRef

> 頻繁變動但不需更新 UI 的值（mouse position、最近一次的計算結果、cancellation flag）必須存在 `useRef.current`，禁止用 `useState` 造成不必要的 re-render。

## 原因

- `useState` 每次 set 都觸發 re-render，高頻變動的值會嚴重拖累效能
- `useRef` 修改不觸發 re-render，適合做 transient 值的容器
- 需要更新畫面時可直接操作對應的 DOM ref，繞過 React 渲染週期

## ❌ Bad

```tsx
// 每次 mousemove 都 re-render
function Tracker() {
  const [lastX, setLastX] = useState(0);

  useEffect(() => {
    const onMove = (event: MouseEvent) => setLastX(event.clientX);
    window.addEventListener('mousemove', onMove);
    return () => window.removeEventListener('mousemove', onMove);
  }, []);

  return <div style={{ transform: `translateX(${lastX}px)` }} />;
}
```

## ✅ Good

```tsx
// 零 re-render,直接操作 DOM
function Tracker() {
  const lastXRef = useRef(0);
  const dotRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const onMove = (event: MouseEvent) => {
      lastXRef.current = event.clientX;
      if (dotRef.current) {
        dotRef.current.style.transform = `translateX(${event.clientX}px)`;
      }
    };
    window.addEventListener('mousemove', onMove);
    return () => window.removeEventListener('mousemove', onMove);
  }, []);

  return <div ref={dotRef} style={{ transform: 'translateX(0px)' }} />;
}
```

## 判斷準則

問自己：「這個值變了，畫面**真的**需要 re-render 嗎？」

- 是 → 用 `useState`
- 否 → 用 `useRef`，需要時直接操作 DOM

## 常見適用場景

- mouse / pointer / scroll position
- 上一次 render 的值（用來做 diff）
- timer / interval ID
- cancellation flag（`cancelledRef.current = true`）
- 第三方 library instance（Chart、Map、Editor）的 reference
