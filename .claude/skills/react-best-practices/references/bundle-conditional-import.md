---
rule: bundle-conditional-import
category: Bundle 拆分與動態載入
tags: [bundle, code-splitting, dynamic-import, lazy]
---

# 大型模組與超過 50KB 元件用動態 import 載入

> 不在首屏需要的大型模組與超過 50KB 的元件（editor、chart、heavy modal、animation frames）必須以動態 `import()` 或 `React.lazy()` 載入，禁止靜態 import 後再用條件式判斷是否使用。

## 原因

- 靜態 import 會把模組納入 main chunk，即使使用者未開啟該功能，仍需承擔下載成本
- TanStack Router 已負責 route 層級的拆分，本規則針對的是「同一個 route 內」的大型元件 / 模組
- `React.lazy()` 配 `<Suspense>` 提供 skeleton。非元件型模組改用 `import()` 在 effect 觸發時載入

## ❌ Bad

```tsx
// animation-frames 即使動畫功能未啟用，仍會被納入 main chunk
import { frames } from './animation-frames';

function AnimationPlayer({ enabled }: { enabled: boolean }) {
  if (!enabled) return null;
  return <Canvas frames={frames} />;
}
```

```tsx
// Monaco Editor 約 300KB，跟著 main chunk 一起下載
import { MonacoEditor } from './monaco-editor';

function CodePanel({ code }: { code: string }) {
  return <MonacoEditor value={code} />;
}
```

## ✅ Good

```tsx
function AnimationPlayer({
  enabled,
  setEnabled,
}: {
  enabled: boolean;
  setEnabled: (value: boolean) => void;
}) {
  const [frames, setFrames] = useState<Frame[] | null>(null);

  useEffect(() => {
    if (!enabled || frames) return;
    let cancelled = false;
    void import('./animation-frames').then(module => {
      if (!cancelled) setFrames(module.frames);
    });
    return () => {
      cancelled = true;
    };
  }, [enabled, frames]);

  if (!frames) return <Skeleton />;
  return <Canvas frames={frames} />;
}
```

```tsx
import { lazy, Suspense } from 'react';

const MonacoEditor = lazy(() =>
  import('./monaco-editor').then(module => ({ default: module.MonacoEditor })),
);

function CodePanel({ code }: { code: string }) {
  return (
    <Suspense fallback={<EditorSkeleton />}>
      <MonacoEditor value={code} />
    </Suspense>
  );
}
```

## 判斷準則

- **元件型且會在 JSX render**：用 `React.lazy()` + `<Suspense>`
- **非元件型（init 函式、工具模組）**：用原生 `import()` 在 effect / event handler / idle 時機載入
- **門檻**：route 層級已由 TanStack Router 處理，元件內部建議只在預估 > 50KB 才額外 lazy，避免過度切分增加 Suspense boundary 複雜度

## Reference

- [React.lazy — load function returns](https://react.dev/reference/react/lazy#load)：官方明訂 `lazy()` 回傳的 Promise 必須 resolve 出 `default` 為合法 component
