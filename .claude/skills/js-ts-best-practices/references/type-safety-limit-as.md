---
rule: type-safety-limit-as
category: type-safety
tags: [type-safety, as, type-assertion, type-guard]
---

# 限制 `as` 斷言，優先 type guard

> 預設禁止 `as` 型別斷言，先用 `typeof`、`instanceof`、`in` 或自訂 type guard 做型別收窄。只在六種白名單情境允許用 `as`。

## 原因

- `as` 跳過編譯器檢查，斷言錯誤要等到 runtime 才會炸
- Type guard 同時是 runtime 檢查與型別收窄，兩者一致
- 限制白名單在安全與便利之間取得平衡

## ❌ Bad

```ts
// 未經檢查直接斷言
function processData(data: unknown) {
  const user = data as User;
  console.log(user.id);
}

// 用 as 繞過型別錯誤
const count: number = someString as unknown as number;

// 可以用 type guard 解決的場景
function getName(input: string | number) {
  return (input as string).toUpperCase();
}
```

## ✅ Good

```ts
// typeof — 原始型別
function formatValue(value: unknown): string {
  if (typeof value === 'string') return value;
  if (typeof value === 'number') return String(value);
  return '';
}

// instanceof — 類別實例
function getErrorMessage(error: unknown): string {
  if (error instanceof Error) return error.message;
  return String(error);
}

// in + 自訂 type guard
function isUser(data: unknown): data is User {
  return (
    typeof data === 'object' &&
    data !== null &&
    'id' in data &&
    'name' in data
  );
}

function processData(data: unknown) {
  if (isUser(data)) {
    console.log(data.id);
  }
}
```

## 例外（六個 `as` 白名單）

1. **`as const` / `as const satisfies`**：const assertion，不是 type assertion，完全安全
2. **測試中的 partial mock**：`const mockUser = { id: 1, name: 'Test' } as User`
3. **DOM 元素型別收窄**：`document.getElementById('email') as HTMLInputElement`
4. **第三方 API 型別不完整時的暫時解法**：`externalLib.getData() as ExpectedType`
5. **框架慣用模式**：Vue `defineEmits` 泛型、React HOC wrapper 等
6. **泛型工廠函式回傳值**：邏輯上可證明正確，但 TS 推不出來時，例如 `return { ...defaults, ...overrides } as T`
