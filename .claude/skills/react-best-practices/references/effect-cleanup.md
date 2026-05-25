---
rule: effect-cleanup
category: Effect 與副作用
tags: [effect, cleanup, memory-leak]
---

# Effect 必須回傳 cleanup function

> 任何在 `useEffect` 內建立的 subscription、event listener、timer、interval、AbortController、observer、WebSocket 連線都必須在 cleanup function 中釋放。

## 原因

- 元件 unmount 或 effect 重跑時，沒清乾淨的訂閱會繼續佔記憶體，造成 leak
- Strict Mode 在 dev 會跑兩次 mount → unmount → mount 以揭露 cleanup 寫錯的情況
- 同一個 effect 重跑時若沒先清掉舊的，舊 listener 不會自動移除，會疊加觸發

## ❌ Bad

```tsx
function Tracker() {
  useEffect(() => {
    const handler = (event: MouseEvent) => console.log(event.clientX);
    window.addEventListener('mousemove', handler);
    // 沒 cleanup，unmount 後 handler 還在
  }, []);
}

function CountdownBanner({ seconds }: { seconds: number }) {
  const [left, setLeft] = useState(seconds);

  useEffect(() => {
    const id = setInterval(() => setLeft(value => value - 1), 1000);
    // 換頁就 leak 一個 interval
  }, []);

  return <div>{left}</div>;
}

function LiveTicker({ symbol }: { symbol: string }) {
  const [tick, setTick] = useState<Tick | null>(null);

  useEffect(() => {
    const socket = new WebSocket(`wss://stream.example/${symbol}`);
    socket.addEventListener('message', event => {
      // 實際專案應用 schema(zod)驗證 event.data 後再 setTick
      setTick(JSON.parse(event.data));
    });
    // symbol 切換時舊 socket 仍在接訊息，setTick 持續被觸發
  }, [symbol]);

  return tick ? <div>{tick.price}</div> : <Spinner />;
}
```

## ✅ Good

```tsx
function Tracker() {
  useEffect(() => {
    const handler = (event: MouseEvent) => console.log(event.clientX);
    window.addEventListener('mousemove', handler);
    return () => window.removeEventListener('mousemove', handler);
  }, []);
}

function CountdownBanner({ seconds }: { seconds: number }) {
  const [left, setLeft] = useState(seconds);

  useEffect(() => {
    const id = setInterval(() => setLeft(value => value - 1), 1000);
    return () => clearInterval(id);
  }, []);

  return <div>{left}</div>;
}

function LiveTicker({ symbol }: { symbol: string }) {
  const [tick, setTick] = useState<Tick | null>(null);

  useEffect(() => {
    const socket = new WebSocket(`wss://stream.example/${symbol}`);
    socket.addEventListener('message', event => {
      setTick(JSON.parse(event.data));
    });
    return () => socket.close();
  }, [symbol]);

  return tick ? <div>{tick.price}</div> : <Spinner />;
}
```

## 需要 cleanup 的清單

- `setTimeout` / `setInterval` → `clearTimeout` / `clearInterval`
- `addEventListener` → `removeEventListener`（必須是同一個 handler reference）
- 訂閱（store、WebSocket、SSE、third-party SDK）→ 對應的 unsubscribe / close
- `IntersectionObserver` / `ResizeObserver` / `MutationObserver` → `observer.disconnect()`
- `fetch` → `AbortController.abort()`
- 動態載入後啟動的計時 / 動畫 → 對應的 stop / cancel

## 例外

- 一次性、同步、不會影響後續 render 的副作用（單純 `console.log` 用於 debug）不需要 cleanup
- 多數資料 fetch 應該交給 TanStack Query，由 library 自己處理 cancellation
