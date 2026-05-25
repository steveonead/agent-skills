---
rule: component-variant-over-boolean
category: 元件設計
tags: [component, api-design, variants, cva]
---

# 變體元件取代 boolean prop 堆疊

> 禁止用多個 boolean prop 控制同一個元件的差異化行為。必須拆成獨立的變體元件，或用 CVA 等 variant 系統定義清楚的離散變體。

## 原因

- `isThread`、`isEditing`、`isDMThread` 堆在一起後變成不可維護的條件地獄
- Boolean flag 之間常有隱性互斥關係，型別系統無法表達
- 變體元件各自組合需要的子元件，邏輯清楚、好讀好測

## ❌ Bad

```tsx
<Composer isThread isDMThread isEditing />;

function Composer({ isThread, isDMThread, isEditing }: Props) {
  return (
    <div>
      {isEditing ? <EditInput /> : <NewInput />}
      {isThread && !isDMThread && <ThreadOptions />}
      {isThread && isDMThread && <AlsoSendToChannel />}
      {!isEditing && <Actions />}
      {isEditing && <EditActions />}
    </div>
  );
}
```

`isThread` 與 `isDMThread` 互斥嗎？`isEditing` 同時為 true 合法嗎？從 props 看不出來。

## ✅ Good

```tsx
function ThreadComposer({ channelId }: { channelId: string }) {
  return (
    <Composer.Frame>
      <Composer.Input />
      <AlsoSendToChannel id={channelId} />
      <Composer.Actions />
    </Composer.Frame>
  );
}

function EditComposer({ messageId }: { messageId: string }) {
  return (
    <Composer.Frame>
      <Composer.Input defaultValue={getMessage(messageId)} />
      <Composer.EditActions />
    </Composer.Frame>
  );
}
```

```tsx
// 若已用 cva，離散變體用 variants 表達
import { cva, type VariantProps } from 'class-variance-authority';

const buttonVariants = cva('inline-flex items-center rounded-md font-medium', {
  variants: {
    intent: {
      primary: 'bg-blue-600 text-white',
      secondary: 'bg-gray-200 text-gray-800',
      danger: 'bg-red-600 text-white',
    },
    size: {
      sm: 'h-8 px-3 text-sm',
      md: 'h-10 px-4 text-base',
      lg: 'h-12 px-6 text-lg',
    },
  },
  defaultVariants: { intent: 'primary', size: 'md' },
});

type ButtonProps = React.ComponentProps<'button'> & VariantProps<typeof buttonVariants>;

function Button({ intent, size, className, ...props }: ButtonProps) {
  return (
    <button className={buttonVariants({ intent, size, className })} {...props} />
  );
}

<Button intent="danger" size="lg">Delete</Button>;
```

當變體數量真的有限且彼此互斥（intent、size、tone），用 CVA / discriminated union 表達；若不同變體會 render 完全不同的子結構，拆成獨立元件比較清楚。
