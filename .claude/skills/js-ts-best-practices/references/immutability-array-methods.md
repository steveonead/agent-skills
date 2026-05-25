---
rule: immutability-array-methods
category: immutability
tags: [immutability, array, side-effect]
---

# 用 immutable 陣列方法

> 處理陣列優先用 `map`、`filter`、`reduce`、`toSorted`、`toReversed`、`toSpliced`、`with`，禁止直接修改原陣列。

## 原因

- 原陣列可能被多處引用，原地修改會在其他引用處產生副作用
- Immutable 方法回傳新陣列，意圖清楚，也讓 React 等需要 reference 比較的場景行為正確
- 函式維持純淨，較容易測試與推理

## ❌ Bad

```ts
const numbers = [3, 1, 2];

const doubled: number[] = [];
for (let i = 0; i < numbers.length; i++) {
  doubled.push(numbers[i] * 2);
}

// sort/reverse/splice 會就地修改原陣列
numbers.sort();
```

`numbers.sort()` 看似回傳排序結果，實際上原陣列已被改寫，其他引用會被影響。

## ✅ Good

```ts
const numbers = [3, 1, 2];

const doubled = numbers.map(value => value * 2);
const evens = numbers.filter(value => value % 2 === 0);

// 對應的 immutable 版本
const sorted = numbers.toSorted();
const reversed = numbers.toReversed();
const replaced = numbers.with(0, 99); // [99, 1, 2]
```

每個操作都回傳新陣列，原陣列保持不動，邏輯線清楚。

## 例外

- 大量資料的熱迴圈、效能敏感場景才考慮原地修改，並需要在註解中說明
