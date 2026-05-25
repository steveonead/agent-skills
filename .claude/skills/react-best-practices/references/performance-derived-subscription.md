---
rule: performance-derived-subscription
category: 效能
tags: [performance, subscription, derived]
---

# 訂閱衍生 boolean 而非連續變動的原始值

> 訂閱外部變動值時，必須訂閱「真正關心的衍生 boolean / enum」，禁止訂閱會持續變動的原始 number（如 `width`、`scrollY`、`mousePosition`）。

## 原因

- 訂閱 `width` 等連續值會在每個 pixel 變化時都 re-render，但元件實際上只關心「是否為 mobile」
- 訂閱衍生 boolean 只會在 true/false 翻轉時 re-render
- 用專門的 hook（`useMediaQuery`、`useBreakpoint`）取代「通用值 + 元件內計算」

## ❌ Bad

```tsx
// 每個 pixel 都 re-render
function Sidebar() {
  const width = useWindowWidth(); // 持續更新
  const isMobile = width < 768;
  return <nav className={isMobile ? 'mobile' : 'desktop'} />;
}
```

## ✅ Good

```tsx
// 只在 boolean 翻轉時 re-render
function Sidebar() {
  const isMobile = useMediaQuery('(max-width: 767px)');
  return <nav className={isMobile ? 'mobile' : 'desktop'} />;
}
```

或自己實作 hook，將訂閱與衍生合併處理：

```tsx
function useIsMobile() {
  const [isMobile, setIsMobile] = useState(
    () => window.matchMedia('(max-width: 767px)').matches,
  );

  useEffect(() => {
    const mql = window.matchMedia('(max-width: 767px)');
    const handler = (event: MediaQueryListEvent) => setIsMobile(event.matches);
    mql.addEventListener('change', handler);
    return () => mql.removeEventListener('change', handler);
  }, []);

  return isMobile;
}
```

## 同類場景

- `scrollY` 連續變動 → 改成「是否已 scroll 過某個 threshold」的 boolean
- `mousePosition` 連續變動 → 改成「是否 hover 在某區塊」的 boolean
- store 中的 array → 用 selector 取衍生 boolean / count，而非整個 array
