---
rule: state-url-search-params
category: 狀態管理
tags: [state, url, search-params, tanstack-router]
---

# 可分享的狀態放 URL search params

> Pagination、sorting、filter、tab、view mode 等使用者**會想分享或加書籤**的狀態必須放 URL search params，禁止放在 component state 或 client store。

## 原因

- URL 天生就是 state manager:可分享、可加書籤、瀏覽器上下頁自動 work
- 使用者重新整理頁面後，filter / pagination / 排序方式不會消失
- URL 作為單一 source of truth，避免 store 與 URL 之間的同步問題

## ❌ Bad

```tsx
// 重新整理就消失，無法分享連結
function UserList() {
  const [page, setPage] = useState(1);
  const [sort, setSort] = useState<'name' | 'date'>('name');
  const [status, setStatus] = useState<string | undefined>();
  // ...
}
```

```ts
// 把 page / sort 放 client store
const useStore = create<Store>()(set => ({
  page: 1,
  sort: 'name',
  // 重新整理一樣消失
}));
```

## ✅ Good

```tsx
// TanStack Router 的 validateSearch，搭配 zod 做型別與驗證
const Route = createFileRoute('/users')({
  validateSearch: z.object({
    page: z.number().default(1),
    sort: z.enum(['name', 'date']).default('name'),
    status: z.enum(['active', 'inactive']).optional(),
  }),
});

function UserList() {
  const { page, sort, status } = Route.useSearch();
  const navigate = Route.useNavigate();

  const handlePageChange = (newPage: number) => {
    void navigate({ search: previous => ({ ...previous, page: newPage }) });
  };

  // 接著用 page / sort / status 組 queryKey 餵給 TanStack Query
}
```

## 狀態歸屬速查

問自己兩個問題:

1. 使用者把這個連結分享出去，對方打開看到的應該是「同樣的畫面」嗎? → 放 URL
2. 使用者重新整理頁面後，這個狀態應該保留嗎? → 放 URL

兩個答案都是「是」就放 URL search params。

## 哪些 **不** 該放 URL

- 一次性的 modal 開合、command palette 顯示 → client store
- 表單欄位的暫存輸入 → 元件 local
- 不需要分享的 sidebar 折疊狀態 → client store 或 localStorage

> 具體 TanStack Router 用法（validateSearch、search middleware、navigate 寫法）由 TanStack Router best practices 處理，本規則只關心「可分享 state 不該存在元件或 store」這條原則。
