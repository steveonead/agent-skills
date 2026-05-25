---
rule: immutability-structured-clone
category: immutability
tags: [immutability, deep-clone, structured-clone]
---

# 深層複製用 `structuredClone` 或 `cloneDeep`

> 需要深層複製時用 `structuredClone`，若專案已用 `es-toolkit` 則統一用 `cloneDeep`，禁止 `JSON.parse(JSON.stringify(...))` 與 spread 假裝深複製。

## 原因

- `JSON.parse(JSON.stringify(...))` 會丟失 `Date`、`Map`、`Set`、`undefined`、函式，並把原本是物件的欄位變成 plain object
- Spread `{...obj}` 只做一層複製，巢狀物件仍共享參考
- `structuredClone` 是 Node 與瀏覽器內建標準 API，正確處理 `Date`/`Map`/`Set`/`RegExp` 與循環引用（部分支援）

## ❌ Bad

```ts
const original = {
  name: 'Alice',
  metadata: { createdAt: new Date(), tags: new Set(['admin']) },
};

// JSON 來回 — Date 變字串，Set 變 {}
const copy = JSON.parse(JSON.stringify(original));

// spread — metadata 仍指向同一個物件
const copy2 = { ...original };
copy2.metadata.tags.add('editor'); // 改到原 original 了
```

JSON 序列化會靜默地丟失特殊型別，spread 則完全沒做深複製。

## ✅ Good

```ts
const original = {
  name: 'Alice',
  metadata: { createdAt: new Date(), tags: new Set(['admin']) },
};

// 一般情況：standard API
const copy = structuredClone(original);
copy.metadata.tags.add('editor'); // 不影響 original

// 若專案已使用 es-toolkit，統一用 cloneDeep
import { cloneDeep } from 'es-toolkit/object';
const copy2 = cloneDeep(original);
```

`structuredClone` 保留所有可結構化複製的型別，`cloneDeep` 對 class instance 與循環引用更穩。

## 例外

- `structuredClone` 無法複製函式、DOM 節點與含原型鏈的 class instance；這些場景需要自行實作複製邏輯
