---
rule: request-set-auth
category: 請求撰寫
tags: [request, set, header, authorization, jwt]
---

# 用 .set() 帶 Authorization header

> token-based 的 auth（例如 JWT）用 `.set('Authorization', ...)` 直接帶 header，token 在 `beforeAll` 取得一次後重複使用，不要每個 test 都重打登入。

## 原因

- JWT 這類 bearer token 是放在 header 而非 cookie，用 `.set()` 帶最直接，也不需要 agent 的 cookie jar。
- 每個 test 都重打一次 `/login` 拿 token，既慢又把 auth endpoint 的狀態耦合進每個案例，登入一旦不穩，全部測試一起失敗。
- 在 `beforeAll` 取一次 token 存起來重複用，測試聚焦在真正要驗證的 endpoint 上。

## ❌ Bad

```ts
it('GET /orders 需要授權', async () => {
  // 每個 test 重打登入拿 token，慢且與 auth endpoint 強耦合
  const login = await request(app.getHttpServer())
    .post('/auth/login')
    .send({ email: 'a@b.c', password: 'pw' });

  await request(app.getHttpServer())
    .get('/orders')
    .set('Authorization', `Bearer ${login.body.token}`)
    .expect(200);
});
```

把登入塞進每個 test，重複成本高，且讓無關的測試案例全都依賴 auth endpoint 的穩定性。

## ✅ Good

```ts
describe('Orders (e2e)', () => {
  let token: string;

  beforeAll(async () => {
    // 直接用 JwtService 簽，或打一次登入，取得後重複用
    token = jwtService.sign({ sub: 'user-1', role: 'admin' });
  });

  it('GET /orders 需要授權', async () => {
    await request(app.getHttpServer())
      .get('/orders')
      .set('Authorization', `Bearer ${token}`)
      .expect(200);
  });
});
```

token 取一次、整個 describe 重複用，每個 test 只負責驗證目標 endpoint。需要測未授權時，省略 `.set()` 斷言 401 即可。

## 補充

- `.set()` 也能用來帶其他 header（如 `Accept`、自訂 header），可鏈式設定多個。
- session-based 的 cookie 流程改用 `request-agent-session`。
