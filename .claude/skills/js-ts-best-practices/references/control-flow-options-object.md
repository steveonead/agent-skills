---
rule: control-flow-options-object
category: control-flow
tags: [control-flow, function-signature, api-design]
---

# 參數超過三個改物件傳遞

> 函式參數超過三個，改用單一 options 物件，並在型別上標清楚必填與選填。

## 原因

- 呼叫端不必記住參數順序，減少錯誤發生的機會
- 加新參數時不影響舊呼叫點，特別是中間加一個選填欄位
- 物件型別本身就是文件，IDE 補全與型別檢查都更有用

## ❌ Bad

```ts
function createUser(
  name: string,
  age: number,
  email: string,
  role: 'admin' | 'member',
) {
  // ...
}

createUser('小明', 25, 'ming@example.com', 'admin');
```

呼叫端容易把 `age` 跟 `email` 順序搞反，加一個 `nickname` 參數就要改所有呼叫點。

## ✅ Good

```ts
type CreateUserOptions = {
  name: string;
  age: number;
  email: string;
  role: 'admin' | 'member';
  nickname?: string;
};

function createUser(options: CreateUserOptions) {
  // ...
}

createUser({
  name: '小明',
  age: 25,
  email: 'ming@example.com',
  role: 'admin',
});
```

每個參數都有名字、有型別，呼叫端讀起來像填表單，加欄位只需擴 type。

## 例外

- 三個以內、語意明確且不會擴增的小工具函式（例如 `clamp(value, min, max)`），用 positional 參數更直覺
