---
rule: type-design-utility-types
category: type-design
tags: [type-design, utility-types, omit, pick, partial]
---

# 善用內建 utility types

> 從既有 type 衍生新型別時，必須使用 `Omit`、`Pick`、`Partial`、`Record`、`ReturnType`、`keyof` 等內建 utility types，禁止手刻重複定義。

## 原因

- 衍生型別跟著原型別走，原型別加欄位時衍生型別自動同步，不會漏掉
- 用 `Omit<User, 'password'>` 比另寫一份 `PublicUser` 表達意圖更清楚
- 內建 utility types 是 TS 慣用法，閱讀者一看就懂

## ❌ Bad

```ts
type User = {
  id: number;
  name: string;
  email: string;
  password: string;
};

// 與 User 重複定義，User 加欄位時這裡會漏掉
type PublicUser = {
  id: number;
  name: string;
  email: string;
};

// 同樣是手刻重複
type UserUpdatePayload = {
  id?: number;
  name?: string;
  email?: string;
  password?: string;
};
```

## ✅ Good

```ts
type User = {
  id: number;
  name: string;
  email: string;
  password: string;
  role: 'admin' | 'user';
};

// Omit — 排除特定屬性
type PublicUser = Omit<User, 'password'>;

// Pick — 只挑選特定屬性
type UserCredentials = Pick<User, 'email' | 'password'>;

// Partial — 所有屬性變選填
type UserUpdatePayload = Partial<User>;

// Record — 鍵值對應
type RolePermissions = Record<User['role'], string[]>;

// keyof — 取出所有屬性名稱的 union
type UserKey = keyof User;

// ReturnType — 取函式回傳型別
function createUser(data: UserUpdatePayload) {
  return { ...data, createdAt: new Date() };
}
type CreateUserResult = ReturnType<typeof createUser>;
```

每種衍生型別都跟原 `User` 綁定，後續維護一致性自動保證。
