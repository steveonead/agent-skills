---
rule: migration-dynamic-module-ref
category: v10 → v11 遷移
tags: [migration, module, dynamic-module]
---

# 動態模組以 object reference 判斷相等

> NestJS 11 不再為動態模組產生可預測的 hash，改用 object reference 判斷兩個模組是否相同，共用時須先指派成變數。

## 原因

- v10 以 metadata 產生的 hash 來辨識動態模組，v11 改以物件參考判斷，效能更好也更省記憶體。
- 在多處各自呼叫 `SomeModule.forRoot(...)` 會產生不同的物件參考，v11 視為不同模組，可能導致重複實例與狀態不一致。
- 要讓多個模組共用同一份動態模組設定，必須建立一次、指派成變數，再到各處 import。

## ❌ Bad

```ts
@Module({
  imports: [ConfigurableModule.forRoot({ folder: './config' })],
})
export class AModule {}

@Module({
  // 又呼叫一次，v11 視為不同的動態模組實例
  imports: [ConfigurableModule.forRoot({ folder: './config' })],
})
export class BModule {}
```

兩次呼叫產生不同物件參考，v11 不會自動去重，造成重複初始化。

## ✅ Good

```ts
// shared-config.ts
export const sharedConfigModule = ConfigurableModule.forRoot({
  folder: './config',
});

@Module({ imports: [sharedConfigModule] })
export class AModule {}

@Module({ imports: [sharedConfigModule] })
export class BModule {}
```

先建立一次並指派成變數，各模組 import 同一個參考，v11 即視為同一個動態模組，正確共用實例。
