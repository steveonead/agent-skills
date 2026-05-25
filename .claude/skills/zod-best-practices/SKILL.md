---
name: zod-best-practices
description: Zod schema 最佳實踐規則集。撰寫、審查或重構 schema 與 validator 時使用，涵蓋 schema 定義、解析驗證與型別推斷，強制使用最新版 API。不適用於 React Hook Form / tRPC 等整合層細節。
---

# Zod 4 Best Practices

這份規則集針對 Zod 4 撰寫，特別強調 v3 → v4 API 的差異。Zod 3 的許多 API（如 `.merge()`、`.strict()`、`z.string().email()`、`invalid_type_error`、`z.nativeEnum()` 等）在 v4 已 deprecate，但 agent 與 LLM 仍傾向沿用舊寫法。規則集把這類 migration 規則集中在 `v4-` 前綴下，確保產出程式碼一律走 v4 API。

## 適用時機

- 撰寫新的 Zod schema 或 validator
- 審查既有 Zod 程式碼是否使用 v4 寫法
- 從 Zod 3 升級到 Zod 4 的 migration 流程
- AI agent 自動產生 Zod schema 時對齊 v4 API

## 規則分類

| 分類 | 前綴 | 條數 |
|------|------|------|
| Zod 4 API 強制（避免 v3 deprecated 寫法） | `v4-` | 8 |
| Schema 定義 | `schema-` | 3 |
| 解析與驗證 | `parse-` | 4 |
| 型別推斷 | `type-` | 2 |
| 錯誤處理 | `error-` | 2 |
| 物件 Schema | `object-` | 3 |
| Refine 與 Transform | `refine-` | 2 |
| 整合能力 | `integration-` | 1 |

## 規則速查

### Zod 4 API 強制

- `v4-top-level-string-formats` — 字串格式用 top-level 函式（`z.email()`、`z.url()`、`z.uuid()`），不用 `z.string().email()` 等 method form
- `v4-iso-date-time` — 日期時間用 `z.iso.date()` / `z.iso.datetime()` / `z.iso.time()` / `z.iso.duration()`，不用 `z.string().datetime()`
- `v4-uuid-vs-guid` — 嚴格 RFC 9562 用 `z.uuid()`；相容 v3 寬鬆語意用 `z.guid()`
- `v4-strict-loose-object` — 用 `z.strictObject()` / `z.looseObject()`，不用 `.strict()` / `.passthrough()` / `.strip()`
- `v4-extend-not-merge` — 物件組合用 `.extend()`，`.merge()` 已 deprecate
- `v4-error-param-unified` — 自訂錯誤統一用 `error` 參數，不用 `invalid_type_error` / `required_error` / `message` / `errorMap`
- `v4-enum-not-nativeenum` — 用 `z.enum()`（含 TS enum），不用 `z.nativeEnum()`
- `v4-default-vs-prefault` — v4 `.default()` 套用時機改變，要還原 v3 行為用 `.prefault()`

### Schema 定義

- `schema-unknown-not-any` — 不確定型別用 `z.unknown()`，不用 `z.any()`
- `schema-avoid-optional-abuse` — 不濫用 `.optional()`，必填欄位就是必填
- `schema-string-validations` — 字串一律加上 `min` / `max` / `regex` / format

### 解析與驗證

- `parse-use-safeparse` — 使用者輸入用 `safeParse()`，不用會 throw 的 `parse()`
- `parse-async-for-async-refinements` — 含 async refine 必用 `parseAsync` / `safeParseAsync`
- `parse-handle-all-issues` — 顯示時彙整 `error.issues`，不只取第一個
- `parse-validate-early` — 邊界一次驗證（API request、JSON、env var），內部信任型別

### 型別推斷

- `type-use-z-infer` — TS 型別一律用 `z.infer<typeof S>`，不手寫 interface
- `type-input-vs-output` — 含 transform 時，輸入端用 `z.input`、輸出端用 `z.infer`

### 錯誤處理

- `error-prettify-and-treeify` — 給使用者看用 `z.prettifyError()`；表單欄位錯誤用 `z.treeifyError()`
- `error-path-for-nested` — 多層欄位錯誤靠 `issue.path` 對應欄位

### 物件 Schema

- `object-partial-pick-omit` — 衍生 schema 用 `.partial()` / `.pick()` / `.omit()`，不重定義
- `object-optional-vs-nullable` — `.optional()`（undefined）與 `.nullable()`（null）語意分清楚
- `object-discriminated-unions` — 標籤式 union 用 `z.discriminatedUnion()`

### Refine 與 Transform

- `refine-vs-superrefine-no-throw` — 多重錯誤用 `.superRefine()`，refine 內 return false 不 throw
- `refine-add-path` — `.refine()` 附上 `path`，錯誤定位到欄位

### 整合能力

- `integration-tojsonschema-for-ai-tools` — AI tool input 或 OpenAPI schema 用 `z.toJSONSchema()`，不手寫

## 使用方式

讀取個別規則檔案以取得詳細說明與範例：

```
references/[類別前綴]-[規則名稱].md
```

每個規則檔案包含：
- 說明此規則重要的原因
- 不建議的寫法（含說明）
- 建議的寫法（含說明）
- 補充說明與參考

## 參考來源

- [Zod 官方文件](https://zod.dev/)
- [Zod 4 Release Notes](https://zod.dev/v4)
- [Zod 4 Migration Guide](https://zod.dev/v4/changelog)
