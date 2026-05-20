---
rule: type-design-discriminated-unions
category: type-design
tags: [type-design, discriminated-union, narrowing, exhaustive-check]
---

# 用判別屬性 + exhaustive check

> 表達多種互斥狀態時，用共用 discriminator 欄位的 union type，配合 `never` 做 exhaustive check。

## 原因

- TypeScript 看到 discriminator 會自動在每個分支收窄型別，不必再 `as` 強轉
- Exhaustive check 讓「新增一種 variant 但忘了處理」變成編譯期錯誤
- 比起選填欄位 + 條件判斷，意圖更清楚、靜態保證更強

## ❌ Bad

```ts
type ApiResult = {
  type: string;
  data?: User;
  message?: string;
  code?: number;
};

function handleResult(result: ApiResult) {
  if (result.type === 'success') {
    // result.data 仍是 User | undefined，型別沒收窄
    console.log(result.data?.name);
  }
  // 新增 type 不會有編譯錯誤提醒
}
```

`data`、`message`、`code` 全是選填，每個分支都要重新判空，新增 variant 也不會被編譯器抓到。

## ✅ Good

```ts
type ApiResult =
  | { type: 'success'; data: User }
  | { type: 'error'; message: string; code: number }
  | { type: 'loading' };

function handleResult(result: ApiResult) {
  switch (result.type) {
    case 'success':
      console.log(result.data.name); // 收窄為 success 分支，data 必存在
      break;
    case 'error':
      console.error(`[${result.code}] ${result.message}`);
      break;
    case 'loading':
      showSpinner();
      break;
    default: {
      const _exhaustive: never = result;
      throw new Error(`Unhandled result type: ${String(_exhaustive)}`);
    }
  }
}
```

新增第四種 variant 時，`_exhaustive: never` 會立刻紅線，強制處理新分支。
