---
rule: type-design-leverage-inference
category: type-design
tags: [type-design, type-inference, annotation]
---

# 讓 TS 推斷，禁冗餘標註

> TypeScript 能推斷的型別就不要手動標註，標註只用在「TS 推不出來」「公開 API 契約」「啟用 `isolatedDeclarations`」等情境。

## 原因

- 冗餘標註只是視覺噪音，閱讀時得多一道對齊
- 標註與實作不一致時，反而會掩蓋真正的問題
- 一律手寫標註會讓後續重構時得多處同步修改

## ❌ Bad

```ts
const count: number = 5;
const name: string = 'Alice';
const isActive: boolean = true;
const users: string[] = ['Alice', 'Bob'];

function add(a: number, b: number): number {
  return a + b;
}
```

每個變數的型別已從右側字面值清楚可見，再標註只是重複。

## ✅ Good

```ts
const count = 5;
const name = 'Alice';
const isActive = true;
const users = ['Alice', 'Bob'];

function add(a: number, b: number) {
  return a + b;
}

const config = {
  apiUrl: '/api',
  timeout: 5000,
} satisfies Record<string, string | number>;
```

## 例外（必須明確標註型別）

- **函式參數**：TS 無法推斷，必須標註
- **公開 API 的回傳型別**：作為契約，避免實作變更時悄悄改變對外型別
- **啟用 `isolatedDeclarations`（TS 5.5+）的專案**：所有 export 的成員（函式、變數、class）都必須顯式標註型別，TS 5.5 後加入此 flag 讓 `.d.ts` 可單檔轉換，是 monorepo 並行建構（如 Bazel、`oxc`）的關鍵
- **先宣告後賦值**：`let result: string;` 後續分支才賦值
