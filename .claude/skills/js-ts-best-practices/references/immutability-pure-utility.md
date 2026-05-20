---
rule: immutability-pure-utility
category: immutability
tags: [immutability, pure-function, side-effect]
---

# Utility function 必須純函式

> Utility function 一律寫成純函式：相同輸入產生相同輸出，不依賴外部狀態、不產生副作用。

## 原因

- 純函式好測，給定輸入就能斷言輸出，不必準備 fixture 或 mock
- 沒有副作用，跨檔案重用時不會把意外的狀態變更帶到別處
- 邏輯只看參數與回傳值，閱讀時不必跨檔追蹤外部變數

## ❌ Bad

```ts
let currentTaxRate = 0.05;

function calculateTotal(items: Item[]): number {
  const subtotal = items.reduce((sum, item) => sum + item.price, 0);
  currentTaxRate = subtotal > 1000 ? 0.1 : 0.05; // 副作用
  return subtotal * (1 + currentTaxRate);
}
```

`calculateTotal` 讀寫模組層級的 `currentTaxRate`，呼叫一次就改一次共享狀態，難以測試也難以平行使用。

## ✅ Good

```ts
const TAX_RATES = { standard: 0.05, premium: 0.1 } as const;

function calculateTotal(items: Item[]): number {
  return items.reduce((sum, item) => sum + item.price, 0);
}

function getTaxRate(subtotal: number): number {
  return subtotal > 1000 ? TAX_RATES.premium : TAX_RATES.standard;
}

function calculateTotalWithTax(items: Item[]): number {
  const subtotal = calculateTotal(items);
  return subtotal * (1 + getTaxRate(subtotal));
}
```

每個函式各自純粹，組合起來表達原本的邏輯，測試與重用都更直接。
