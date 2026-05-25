---
rule: component-shared-state
category: 元件設計
tags: [component, props-drilling, composition, compound, zustand]
---

# 跨層狀態共享:composition / compound / store

> Props 傳遞禁止超過 2 層。需要跨層共享狀態時，依場景挑選：composition（children）、Compound Components、或 client state store。

## 原因

- 深層 prop drilling 讓中間層被迫傳遞自己用不到的 props，重構與測試都變難
- 三種解法各有適用場景，選最簡單能達成目的的那個就好
- Server data 與可分享 state 不在本規則範圍（分別由 server-state cache 與 URL search params 處理）

## 三種解法的選擇

| 解法 | 適用場景 | 範例 |
| --- | --- | --- |
| Composition（children） | 子元件需要父層資料，結構單純 | 把子元件直接傳進 children，而非把 data 傳下去 |
| Compound Components | 同一個元件家族要共享內部 state，外部負責組合 UI | `<Composer.Provider>` 配 `<Composer.Input>` / `<Composer.Actions>` |
| Client state store（Zustand） | 真正的全域 UI 狀態（sidebar、modal、theme） | 在需要的元件 selector 取用 |

## ❌ Bad

```tsx
// 三層 prop drilling
<Page user={user} onLogout={onLogout}>
  <Layout user={user} onLogout={onLogout}>
    <Header user={user} onLogout={onLogout}>
      <UserMenu user={user} onLogout={onLogout} />
    </Header>
  </Layout>
</Page>
```

## ✅ Good — Composition

```tsx
// 父層直接組好，中間層不需要知道內容
<Page>
  <Layout>
    <Header>
      <UserMenu user={user} onLogout={onLogout} />
    </Header>
  </Layout>
</Page>
```

## ✅ Good — Compound Components

```tsx
type ComposerContext = {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
};

const ComposerCtx = createContext<ComposerContext | null>(null);

function useComposer() {
  const ctx = use(ComposerCtx);
  if (!ctx) throw new Error('useComposer 必須在 <Composer.Provider> 內使用');
  return ctx;
}

function Provider({ children }: { children: React.ReactNode }) {
  const [value, setValue] = useState('');
  const handleSubmit = () => {
    /* submit */
  };
  return (
    <ComposerCtx value={{ value, onChange: setValue, onSubmit: handleSubmit }}>
      {children}
    </ComposerCtx>
  );
}

function Input() {
  const { value, onChange } = useComposer();
  return <input value={value} onChange={event => onChange(event.target.value)} />;
}

function Actions() {
  const { onSubmit } = useComposer();
  return <button onClick={onSubmit}>Send</button>;
}

export const Composer = { Provider, Input, Actions };

// 使用端自由組合
<Composer.Provider>
  <Composer.Input />
  <AlsoSendToChannel id={channelId} />
  <Composer.Actions />
</Composer.Provider>;
```

## ✅ Good — Client state store

```tsx
// 跨多層、跨頁面的純 UI state
const useUIStore = create<UIState>()(set => ({
  sidebarOpen: true,
  toggleSidebar: () => set(state => ({ sidebarOpen: !state.sidebarOpen })),
}));

function SidebarToggle() {
  const toggleSidebar = useUIStore(state => state.toggleSidebar);
  return <button onClick={toggleSidebar}>切換側欄</button>;
}
```
