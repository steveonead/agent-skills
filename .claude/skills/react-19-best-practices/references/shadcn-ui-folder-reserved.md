---
rule: shadcn-ui-folder-reserved
category: shadcn/UI 整合
tags: [shadcn, file-organization]
---

# components/ui/ 只放 shadcn 原始元件

> `components/ui/` 只放 shadcn 透過 CLI generated 的原始元件（Button、Dialog、Input 等）。業務元件必須放 `components/` 或 `features/*/components/`。

## 原因

- 混在一起後分不清哪些是 shadcn 的、哪些是自己寫的，regenerate 時無法判斷哪些可以安全覆蓋
- 清楚的目錄分層讓新人快速理解專案架構
- 與 `shadcn diff` 工具的假設一致:它預設 `components/ui/` 與上游同源

## 目錄職責

| 目錄 | 內容 | 範例 |
| --- | --- | --- |
| `components/ui/` | shadcn 原始元件 | `button.tsx`、`dialog.tsx`、`input.tsx` |
| `components/` | 跨 feature 共用的業務元件 | `app-button.tsx`、`user-card.tsx`、`page-header.tsx` |
| `features/*/components/` | 特定功能模組的元件 | `features/orders/components/order-table.tsx` |

## ❌ Bad

```
src/
├── components/
│   ├── ui/
│   │   ├── button.tsx          ✓ shadcn
│   │   ├── dialog.tsx          ✓ shadcn
│   │   ├── app-button.tsx      ✗ 業務元件混進來
│   │   └── order-table.tsx     ✗ feature 元件混進來
```

## ✅ Good

```
src/
├── components/
│   ├── ui/                     # shadcn 原始元件
│   │   ├── button.tsx
│   │   ├── dialog.tsx
│   │   └── input.tsx
│   ├── app-button.tsx          # 共用業務元件
│   └── user-card.tsx
└── features/
    └── orders/
        └── components/
            └── order-table.tsx # 功能模組元件
```

## 命名建議

業務元件用 `app-` 或具體業務名稱前綴，明確區分 shadcn 與自家元件:

- `Button`（shadcn）→ `AppButton`（多包了 loading state、業務樣式預設）
- `Dialog`（shadcn）→ `ConfirmDialog`（特定情境的封裝）
