---
rule: effect-event-handler
category: Effect 與副作用
tags: [effect, event-handler, anti-pattern]
---

# 互動邏輯放 event handler

> 使用者操作觸發的 side effect（送出表單、發 analytics、開 modal）必須直接在 event handler 內執行，禁止用 state + `useEffect` 模擬事件。

## 原因

- state + effect 模擬事件會把無關依賴拖進來（例如 theme 變了也會重跑 effect）
- Event handler 明確表達「使用者做了 X → 執行 Y」的因果，比 state 同步好讀
- 減少不必要的 effect 與 state，元件結構更乾淨

## ❌ Bad

```tsx
function Form() {
  const [submitted, setSubmitted] = useState(false);
  const theme = useContext(ThemeContext);

  // 用 state + effect 模擬事件
  useEffect(() => {
    if (submitted) {
      post('/api/register');
      showToast('Registered', theme);
    }
  }, [submitted, theme]); // theme 變了也會重跑!

  return <button onClick={() => setSubmitted(true)}>Submit</button>;
}
```

## ✅ Good

```tsx
function Form() {
  const theme = useContext(ThemeContext);

  function handleSubmit() {
    post('/api/register');
    showToast('Registered', theme);
  }

  return <button onClick={handleSubmit}>Submit</button>;
}
```

## 判斷準則

問自己：「這段邏輯是因為**誰**而觸發？」

- 因為「使用者按了按鈕」→ event handler
- 因為「某個 state / prop 變了」→ effect，但要再問一次值不值得用 effect（多數時候可以在 render 算）
- 因為「app 起動 / 元件 mount」→ effect 或 module scope
