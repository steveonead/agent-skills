---
rule: query-no-derived-state
category: Query 資料管理
tags: [query, state, derived-state, useEffect, anti-pattern]
---

# 不要把 query data 同步進 `useState` 或外部 store

> 在 `useEffect` 內 `setState(data)` 把 query 結果搬進 local state，或同步進 Zustand / Redux，會立刻產生 stale derived state。需要衍生值用 `select`，需要互動暫存用 form state，不要把 cache 鏡像化。

## 原因

- TanStack Query 本身即為 cache，再另開一份 `useState` 等同於存在兩個事實來源，refetch 或 invalidate 後 local state 將持續落後一個更新週期
- 衍生值（filter、map、sort）應於 `useSuspenseQuery({ ..., select })` 的 subscription 層處理，TanStack Query 的 structural sharing 會保持 reference 穩定
- Form 編輯這類需要 dirty state 的場景應使用 form library 管理 draft state，而非以 `useEffect` 同步 server data

## ❌ Bad

```tsx
function UserEditor({ id }: { id: string }) {
  const { data: user } = useSuspenseQuery(userDetailOptions(id));
  const [name, setName] = useState("");

  // refetch 完成或 cache invalidate 後，name 仍為舊值
  useEffect(() => {
    setName(user.name);
  }, [user]);

  return (
    <input value={name} onChange={(event) => setName(event.target.value)} />
  );
}
```

```tsx
// 把 query data 同步進 Zustand store
const { data: users } = useSuspenseQuery(userListOptions());
useEffect(() => {
  useUserStore.setState({ users });
}, [users]);
```

## ✅ Good

```tsx
// 衍生值用 select
function UserName({ id }: { id: string }) {
  const name = useSuspenseQuery({
    ...userDetailOptions(id),
    select: (user) => user.name,
  }).data;
  return <span>{name}</span>;
}

// 表單編輯用 form library 管 draft，提交時送 mutation
function UserEditor({ id }: { id: string }) {
  const { data: user } = useSuspenseQuery(userDetailOptions(id));
  const form = useForm({ defaultValues: user });
  const mutation = useMutation({ mutationFn: updateUser });

  return (
    <form onSubmit={form.handleSubmit(mutation.mutate)}>
      <input {...form.register("name")} />
    </form>
  );
}
```

## 例外

純 UI state（modal 開關、選取的 row id、tooltip 顯示）與 server data 無關，本來就應該使用 `useState`。核心原則是「不要鏡像 server data」。
