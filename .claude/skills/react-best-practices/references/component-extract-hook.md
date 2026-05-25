---
rule: component-extract-hook
category: 元件設計
tags: [component, custom-hook, separation-of-concerns]
---

# 邏輯抽 custom hook,元件保持薄

> 同一個元件不該同時承擔 UI render、資料 fetch、訂閱、複雜運算與業務規則。任何**會跨元件重用**或**需要獨立測試**的非 render 邏輯，必須抽成 custom hook。

## 原因

- 一個元件吃下所有責任時，會變成 500–800 行的 god component，PR 變大、衝突變多
- 邏輯與 UI 綁在一起就難以單元測試，最後只能寫脆弱的 E2E
- Custom hook 是 React 的標準抽象單位，能在保留 hook 規則的前提下重用邏輯

## ❌ Bad

```tsx
type SortKey = 'name' | 'createdAt';

function UserList() {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [sortKey, setSortKey] = useState<SortKey>('name');

  useEffect(() => {
    setIsLoading(true);
    fetch(`/api/users?search=${search}`)
      .then(response => response.json())
      .then(data => {
        setUsers(data);
        setIsLoading(false);
      });
  }, [search]);

  const sorted = [...users].sort((a, b) => {
    if (sortKey === 'name') return a.name.localeCompare(b.name);
    return b.createdAt - a.createdAt;
  });

  if (isLoading) return <Spinner />;
  return (
    <div>
      <input value={search} onChange={event => setSearch(event.target.value)} />
      <button onClick={() => setSortKey('name')}>姓名</button>
      <button onClick={() => setSortKey('createdAt')}>建立時間</button>
      <ul>{sorted.map(user => <li key={user.id}>{user.name}</li>)}</ul>
    </div>
  );
}
```

UI、search state、資料 fetch 與排序邏輯全部混雜在一起，難以測試也難以重用。

## ✅ Good

```tsx
// 1. 資料層:server state 用 TanStack Query
function useUsersQuery(search: string) {
  return useQuery({
    queryKey: ['users', { search }],
    queryFn: () => fetchUsers(search),
  });
}

// 2. 排序邏輯:純 function 或 hook
type SortKey = 'name' | 'createdAt';

function useSortedUsers(users: User[], sortKey: SortKey) {
  return [...users].sort((a, b) => {
    if (sortKey === 'name') return a.name.localeCompare(b.name);
    return b.createdAt - a.createdAt;
  });
}

// 3. 元件保持薄，只負責 render 與輸入流
function UserList() {
  const [search, setSearch] = useState('');
  const [sortKey, setSortKey] = useState<SortKey>('name');
  const { data: users = [], isPending } = useUsersQuery(search);
  const sorted = useSortedUsers(users, sortKey);

  if (isPending) return <Spinner />;
  return (
    <div>
      <input value={search} onChange={event => setSearch(event.target.value)} />
      <button onClick={() => setSortKey('name')}>姓名</button>
      <button onClick={() => setSortKey('createdAt')}>建立時間</button>
      <ul>{sorted.map(user => <li key={user.id}>{user.name}</li>)}</ul>
    </div>
  );
}
```

## 抽 hook 的判斷準則

- 同樣的 `useState + useEffect` 在多個元件出現 → 抽
- 一段邏輯需要單獨寫測試 → 抽
- 元件內有「副作用 + state 同步 + 衍生計算」三件事其中至少兩件 → 抽
- 純衍生值（filter、sort、format）可以直接在 render 算，不一定要抽 hook

## 例外

- 真的只在一個元件用一次的邏輯，不必為了「未來可能會用」先抽。等到第二次需求出現再抽。
