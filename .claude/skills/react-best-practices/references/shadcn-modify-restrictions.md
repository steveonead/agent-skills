---
rule: shadcn-modify-restrictions
category: shadcn/UI 整合
tags: [shadcn, customization, wrapper]
---

# 限制直接修改 shadcn 原始碼的場景

> 預設用 wrapper 元件擴展行為，禁止直接修改 `components/ui/` 下的 shadcn 原始碼。只有以下情境允許直接編輯:新增 CVA variants / sizes、改內部 DOM 結構或預設 Tailwind class、修正 a11y / 語意 HTML、移除未使用程式碼、轉發未暴露的 sub-component props。

## 原因

- 直接改原始碼後，shadcn upstream 更新或 regenerate 會覆蓋掉改動
- Wrapper 讓 shadcn 原始與自家邏輯分得清，diff 時不會被噪音淹沒
- 白名單外的場景，wrapper 一定能達成；白名單內的場景，wrapper 反而做不到或會造成複雜的覆蓋鏈

## 允許直接編輯的場景

1. **新增或修改 CVA variants / sizes**:Wrapper 無法注入新 variant 到 CVA 定義
2. **修改內部 DOM 結構或預設 Tailwind class**:Wrapper 改不了內部元素層級;Tailwind Merge 對 pseudo selector 與 compound selector 處理有極限
3. **修正 a11y / 語意 HTML**:Wrapper 改不了內部 ARIA、focus 管理、語意 element 選擇
4. **移除未使用程式碼 / 效能優化**:減少 bundle size，wrapper 反而增加開銷
5. **轉發上游未暴露的 sub-component props**:必須在原始碼新增 prop 轉發，wrapper 觸及不到內部 primitive

白名單以外都用 wrapper。

## ❌ Bad

```tsx
// components/ui/button.tsx — 白名單以外加 loading 邏輯，upgrade 會被覆蓋
function Button({ loading, children, ...props }: ButtonProps & { loading?: boolean }) {
  return <button {...props}>{loading ? <Spinner /> : children}</button>;
}
```

## ✅ Good — Wrapper

```tsx
// components/app-button.tsx
import { Button, type ButtonProps } from '@/components/ui/button';

type AppButtonProps = ButtonProps & {
  loading?: boolean;
};

function AppButton({ loading, children, disabled, ...props }: AppButtonProps) {
  return (
    <Button disabled={disabled || loading} {...props}>
      {loading ? <Spinner /> : children}
    </Button>
  );
}
```

## ✅ Good — 白名單情境的直接編輯

```tsx
// components/ui/button.tsx — 新增 brand variant 與 xs size
const buttonVariants = cva('...', {
  variants: {
    variant: {
      default: '...',
      brand: 'bg-brand-500 text-white hover:bg-brand-600', // CUSTOMIZED: 公司品牌色
    },
    size: {
      default: '...',
      xs: 'h-6 px-2 text-xs', // CUSTOMIZED: 表格 inline 操作用
    },
  },
});
```

## 修改後的維護義務

直接修改 shadcn 原始碼後，必須:

- 在修改處加上 `// CUSTOMIZED:` 註解說明原因
- 用 `npx shadcn@latest diff` 定期比對 upstream 變更
- 修改了語意或 a11y 時，重新測鍵盤操作與螢幕閱讀器
