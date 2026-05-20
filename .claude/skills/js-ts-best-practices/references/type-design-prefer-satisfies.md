---
rule: type-design-prefer-satisfies
category: type-design
tags: [type-design, satisfies, type-inference]
---

# 需檢查又想保留推斷時用 `satisfies`

> 要驗證物件符合某個型別、又想保留實際內容的精確推斷時，用 `satisfies` 而非型別標註 `:`。

## 原因

- 型別標註 `:` 會把變數型別寬化為標註的那個型別，丟失字面值資訊
- `satisfies` 只做檢查，不改變實際推斷型別，保留所有額外資訊
- 額外屬性也能照常存取，編譯期仍會驗證物件符合契約

## ❌ Bad

```ts
const axis: { x: number; y: number } = {
  x: 1,
  y: 2,
  extra: 3, // 型別錯誤，標註不允許額外屬性
};

// 即使不加 extra，axis.x 型別只是 number，失去字面值 1 的資訊
const palette: Record<string, string> = {
  primary: '#0f0',
  secondary: '#f00',
};
palette.primary; // 推斷為 string，不是 '#0f0'
```

## ✅ Good

```ts
const axis = {
  x: 1,
  y: 2,
  extra: 3,
} satisfies { x: number; y: number };

axis.extra; // OK，型別為 number

const palette = {
  primary: '#0f0',
  secondary: '#f00',
} satisfies Record<string, string>;

palette.primary; // 推斷為 '#0f0'，保留字面值
```

`satisfies` 同時做到「檢查符合型別」與「保留實際推斷」，是型別標註的更精確替代。
