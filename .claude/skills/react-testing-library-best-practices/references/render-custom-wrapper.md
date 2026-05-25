---
rule: render-custom-wrapper
category: render 進階用法
tags: [render, wrapper, providers]
---

# 用 custom render 集中包 providers

> 把 Router、Query Client、Theme 等 provider 收進一個 custom render，測試只 import 這個 render，不在每個測試手動疊 provider。

## 原因

- 元件常同時依賴多個 context，每個測試各自包 provider 會重複又容易遺漏。
- 集中在一處，provider 設定（例如每次 render 給一個全新的 QueryClient）才一致，避免測試之間共用狀態互相污染。
- custom render 可包裝原 render 的 options，並透過 `wrapper` option 疊加，仍回傳完整 query 結果。

## ❌ Bad

```tsx
test('顯示清單', () => {
  render(
    <QueryClientProvider client={new QueryClient()}>
      <MemoryRouter>
        <ThemeProvider>
          <List />
        </ThemeProvider>
      </MemoryRouter>
    </QueryClientProvider>,
  )
})
```

每個測試都重複撰寫一遍 provider 樹，難維護。

## ✅ Good

```tsx
// test-utils.tsx
import { render, type RenderOptions } from '@testing-library/react'
import { type ReactElement, type ReactNode } from 'react'

function AllProviders({ children }: { children: ReactNode }) {
  const queryClient = new QueryClient() // 每次 render 給乾淨的 client
  return (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <ThemeProvider>{children}</ThemeProvider>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

export function renderWithProviders(ui: ReactElement, options?: RenderOptions) {
  return render(ui, { wrapper: AllProviders, ...options })
}
```

測試只 `import { renderWithProviders }` 並呼叫它，需要時還能用 options 覆寫。
