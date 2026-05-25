---
rule: state-server-cache
category: 狀態管理
tags: [state, server-state, tanstack-query]
---

# Server data 交給 server-state cache，禁止存進 client store

> API response、列表資料、單筆內容必須由 server-state cache（TanStack Query）管理。禁止手動把 server data 放進 `useState`、Zustand store 或自己刻 fetch + state 同步。

## 原因

- Server-state cache 已內建 dedup、background refetch、cache invalidation、retry，自己刻只會做出更差的版本
- 同份 server data 放進兩個地方（store + cache），永遠會 out-of-sync
- Server data 的生命週期是 stale → fetching → fresh，跟 client UI state 完全不同

## ❌ Bad

```ts
// 手動實作 fetch + state，沒有 retry / cache / dedup
const useStore = create<Store>()(set => ({
  users: [],
  loading: false,
  actions: {
    fetchUsers: async () => {
      set({ loading: true });
      const users = await fetch('/api/users').then(response => response.json());
      set({ users, loading: false });
    },
  },
}));
```

```tsx
// 用 useEffect + useState 手刻 fetch
function UserList() {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setIsLoading(true);
    fetch('/api/users')
      .then(response => response.json())
      .then(data => {
        setUsers(data);
        setIsLoading(false);
      });
  }, []);
}
```

## ✅ Good

```tsx
// queryOptions 集中管 queryKey + queryFn，跨元件共用
function userListOptions() {
  return queryOptions({
    queryKey: ['users', 'list'],
    queryFn: fetchUsers,
  });
}

function UserList() {
  const { data: users } = useSuspenseQuery(userListOptions());
  return (
    <ul>
      {users.map(user => <li key={user.id}>{user.name}</li>)}
    </ul>
  );
}
```

## 為什麼不該「順手」放進 store

當你想著「把這筆資料放進 store 比較好取用」時，其實常常代表:

- 你想跨元件共用同份資料 → TanStack Query 用同一個 queryKey 已經能做
- 你想避免重複請求 → cache 已經處理
- 你想 optimistic update → 用 `queryClient.setQueryData` 或 `useMutation` 的 `onMutate`

幾乎所有「為什麼要放 store」的需求都能用 server-state cache 內建機制解決。

> 具體 TanStack Query 用法（queryKey 命名、mutation pattern、optimistic update）由 TanStack Query best practices 處理，本規則只關心「server data 不該手動存 client store」這條原則。
