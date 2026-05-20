---
rule: control-flow-lookup-table
category: control-flow
tags: [control-flow, lookup-table, refactor]
---

# 多條件對應改用 Object/Map 查找

> 「輸入對應到輸出」這種純查表邏輯，用 `Record`、`Map` 或 `as const` 物件取代 `if-else` 或 `switch`。

## 原因

- 查表的資料結構與邏輯分離，新增 case 只是多一筆資料，不必動程式控制流
- 配合 `Record<Key, Value>` 型別，能在編譯期確保所有 key 都有對應值
- 對「型別決定行為」的場景，查表比 `switch` 更不容易遺漏 case

## ❌ Bad

```ts
type Status = 'pending' | 'success' | 'fail' | 'unknown';

function getStatusColor(status: Status): string {
  if (status === 'pending') {
    return 'yellow';
  } else if (status === 'success') {
    return 'green';
  } else if (status === 'fail') {
    return 'red';
  } else {
    return 'gray';
  }
}
```

新增一個 status 要動函式本體，加分支也容易漏掉某個 case 而沒有編譯期警告。

## ✅ Good

```ts
type Status = 'pending' | 'success' | 'fail' | 'unknown';

const STATUS_COLORS: Record<Status, string> = {
  pending: 'yellow',
  success: 'green',
  fail: 'red',
  unknown: 'gray',
};

function getStatusColor(status: Status): string {
  return STATUS_COLORS[status];
}
```

`Record<Status, string>` 強制所有 status 都要對應顏色，少一個 key 編譯就失敗。

## 例外

- 條件本身需要計算或範圍比較（如 `age < 18` / `age >= 65`），不是純鍵值對應，這時 `if-else` 反而更清楚
- 每個分支有額外副作用，不只是 return 值，例如分支會呼叫不同的 service
