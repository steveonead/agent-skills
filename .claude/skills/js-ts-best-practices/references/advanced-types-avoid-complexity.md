---
rule: advanced-types-avoid-complexity
category: advanced-types
tags: [advanced-types, complexity, maintainability]
---

# 避免過度複雜的型別

> 高階型別技巧（巢狀 conditional、deep recursive、長串 template literal）只在真正必要時使用。型別寫到難以理解時，優先簡化或拆解。

## 原因

- 過度複雜的型別會拖慢 TS 編譯與 IDE 補全，整個專案的開發體驗變差
- 後續維護者讀不懂的型別等同沒型別，反而成為負擔
- 大多數應用層程式不需要遞迴或極致的型別程式設計，框架/函式庫作者才比較常用

## ❌ Bad

```ts
// 深度遞迴 + conditional + key 變形，讀起來像加密
type DeepCamelCase<T> = T extends object
  ? {
      [K in keyof T as K extends string
        ? CamelCase<K>
        : K]: T[K] extends object ? DeepCamelCase<T[K]> : T[K];
    }
  : T;

// 為了支援所有可能 case，型別寫到 200 行
type ComplexQuery<T> = /* ... 大量條件分支 ... */;
```

只有少數場景真的需要這種型別，但維護成本永遠在那裡，編譯也會明顯變慢。

## ✅ Good

```ts
// 把複雜邏輯拆成幾個小型別，逐步推導
type CamelCaseKey<K extends string> = K extends `${infer Head}_${infer Tail}`
  ? `${Head}${Capitalize<CamelCaseKey<Tail>>}`
  : K;

type CamelCaseObject<T> = {
  [K in keyof T as K extends string ? CamelCaseKey<K> : K]: T[K];
};

// 或者：如果不是 lib 作者，直接寫具體型別
type ApiResponse = {
  userId: string;
  createdAt: string;
};
```

把巨大型別拆成幾個有名字的小型別，閱讀者可以一段一段看懂；應用層多數場景直接寫具體型別就好。

## 例外

- 函式庫作者撰寫公開 API 時，為了使用端的體驗，複雜型別有其必要
