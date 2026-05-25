---
name: js-ts-best-practices
description: JavaScript / TypeScript 最佳實踐規則集。撰寫、審查或重構 JS/TS 程式碼時使用，涵蓋命名、控制流程、不可變、模組、型別設計與型別安全。會先偵測 codebase 是否含 TS，純 JS 專案自動略過型別規則。
---

# JavaScript / TypeScript Best Practices

這份規則集涵蓋 JS/TS 在命名、控制流程、不可變、模組、型別設計、型別安全與進階型別七大面向的實戰規則。

## 適用時機

參考這份規則集的時機：
- 撰寫新的 JS/TS 程式碼
- 審查既有程式碼的品質（PR self-review、code review）
- 重構或最佳化既有程式碼

## 前置偵測：JS 或 TS？

使用本 skill 前，先判斷 codebase 是否含 TypeScript：

1. **檢查 root 是否有 `tsconfig.json`**（含 `tsconfig.base.json`、`tsconfig.*.json` 變體）
2. **若無，再 glob 是否存在任何 `.ts` / `.tsx` 檔案**（排除 `node_modules`、`dist`、`build`）

判定結果決定適用範圍：

| 結果 | 適用範圍 |
|------|---------|
| 含 TS | 全部七大類規則 |
| 純 JS | 僅 `naming-*`、`control-flow-*`、`immutability-*`、`module-*` 四類；略過標 `[TS]` 的 `type-design-*`、`type-safety-*`、`advanced-types-*` |

混合專案（同時有 `.js` 與 `.ts`）視為含 TS。

## 規則分類

| 分類 | 前綴 | 規則數 | 適用 |
|------|------|--------|------|
| 命名與可讀性 | `naming-` | 3 | JS / TS |
| 控制流程 | `control-flow-` | 6 | JS / TS |
| 不可變與純粹 | `immutability-` | 4 | JS / TS |
| 模組系統 | `module-` | 2 | JS / TS |
| 型別設計 | `type-design-` | 6 | TS only |
| 型別安全 | `type-safety-` | 3 | TS only |
| 進階型別技巧 | `advanced-types-` | 3 | TS only |

## 規則速查

### 命名與可讀性

- `naming-function-declaration` — 具名函式用 `function`，callback 用 arrow
- `naming-callback-no-abbr` — Callback 參數禁用單字母或縮寫
- `naming-no-magic-values` — 消除魔術數字與字串

### 控制流程

- `control-flow-early-return` — 邊界條件 early return，禁深層巢狀
- `control-flow-lookup-table` — 多條件對應改用 Object/Map 查找
- `control-flow-optional-nullish` — 用 `?.` 與 `??`，避開 `||` 的 falsy 陷阱
- `control-flow-options-object` — 參數超過三個改物件傳遞
- `control-flow-explicit-errors` — 禁止靜默失敗
- `control-flow-parallel-promises` — 獨立非同步操作用 `Promise.all` 或 `Promise.allSettled`

### 不可變與純粹

- `immutability-array-methods` — 用 immutable 陣列方法
- `immutability-pure-utility` — Utility function 必須純函式
- `immutability-prefer-map-set` — 用 `Map`/`Set` 取代物件/陣列模擬
- `immutability-structured-clone` — 深層複製用 `structuredClone` 或 `cloneDeep`

### 模組系統

- `module-named-exports` — 優先 named export（白名單：單一元件）
- `module-limit-barrel` — 限制 barrel export，禁 `export *`

### 型別設計 `[TS]`

- `type-design-precise-types` — 用 literal/template literal/tuple/branded 取代寬鬆型別
- `type-design-no-enum` — 禁 `enum`，改 `as const`
- `type-design-utility-types` — 善用內建 utility types
- `type-design-discriminated-unions` — 用判別屬性 + exhaustive check
- `type-design-prefer-satisfies` — 需檢查又想保留推斷時用 `satisfies`
- `type-design-leverage-inference` — 讓 TS 推斷，禁冗餘標註

### 型別安全 `[TS]`

- `type-safety-limit-as` — 限制 `as` 斷言，優先 type guard
- `type-safety-readonly` — 用 `Readonly`/`readonly` 在編譯期防修改
- `type-safety-generics-extends` — 泛型用 `extends` 限制範圍

### 進階型別技巧 `[TS]`

- `advanced-types-custom-type-guards` — 自訂 type guard 封裝重複收窄
- `advanced-types-assertion-functions` — 用 assertion function 取代手寫 throw + 轉型
- `advanced-types-avoid-complexity` — 避免過度複雜的型別

## 使用方式

讀取個別規則檔案以取得詳細說明與範例：

```
references/<類別前綴>-<規則名稱>.md
```

每個規則檔案包含：
- 說明此規則重要的原因
- 不建議的寫法（含說明）
- 建議的寫法（含說明）
- 補充說明與參考
