---
rule: types-test-api
category: 型別測試
tags: [types, expectTypeOf, assertType, typecheck]
---

# 型別測試用 `expectTypeOf` / `assertType`

> 要驗證型別推斷正確（泛型回傳、函式簽名、條件型別），用 `expectTypeOf` 或 `assertType` 寫型別層級斷言，並開啟 `typecheck`。這些斷言在執行期不做任何事，全靠 type checker 驗證。

## 原因

- 型別正確性無法靠 runtime 斷言驗證，`expectTypeOf` 才能在 type 層級檢查
- 對外公開的 API 型別退化時，型別測試會在 typecheck 階段直接失敗
- `assertType` 搭配 `@ts-expect-error` 可斷言「這個用法應該要型別錯誤」

## ❌ Bad

```ts
test('returns string', () => {
  const result = parse('42')
  // 只驗了 runtime 值，型別推成 any / unknown 也測不出來
  expect(typeof result).toBe('string')
})
```

## ✅ Good

```ts
import { assertType, expectTypeOf, test } from 'vitest'

test('parse 的型別正確', () => {
  expectTypeOf(parse).toBeFunction()
  expectTypeOf(parse).parameter(0).toExtend<string>()
  expectTypeOf(parse('42')).toEqualTypeOf<number>()

  // @ts-expect-error 參數必須是 string
  assertType(parse(42))
})
```

型別測試需在 config 開啟 `test.typecheck`（或用 `vitest typecheck` 執行），否則型別斷言不會被檢查。
