---
rule: request-agent-session
category: 請求撰寫
tags: [request, agent, cookie, session, auth]
---

# 需要維持 cookie / session 時用 request.agent()

> 測試需要跨請求保留 cookie（例如登入後存取受保護資源）時，用 `request.agent(server)` 建立持久 agent，它會自動帶上前一個回應 set 的 cookie。

## 原因

- 直接用 `request(server)` 時，每個 `.get()` / `.post()` 都是獨立請求，不會記住上一個回應的 cookie，登入後的請求等於未登入。
- `request.agent(server)` 維持一個 cookie jar，登入請求拿到 `Set-Cookie` 後，後續請求會自動帶回去，貼近真實瀏覽器行為。
- 這對 session-based 的 auth 流程特別重要，能省去每個請求手動搬 cookie 的麻煩。

## ❌ Bad

```ts
it('登入後可存取 profile', async () => {
  await request(app.getHttpServer())
    .post('/login')
    .send({ username: 'tobi', password: 'secret' })
    .expect(200);

  // 換一個全新的 request，cookie 沒被帶過來，被擋在 401
  await request(app.getHttpServer())
    .get('/profile')
    .expect(200); // 實際上回 401
});
```

兩個請求各自獨立，登入拿到的 session cookie 沒被第二個請求帶上，受保護路由直接 401。

## ✅ Good

```ts
it('登入後可存取 profile', async () => {
  const agent = request.agent(app.getHttpServer());

  await agent
    .post('/login')
    .send({ username: 'tobi', password: 'secret' })
    .expect(200);

  // 同一個 agent，cookie 自動帶上
  await agent
    .get('/profile')
    .expect(200);
});
```

用同一個 agent 串起整段流程，cookie 在請求之間自動延續，測到的就是真實的登入後行為。

## 補充

- v7.0 修正了 `TestAgent` 不繼承 `Agent` 屬性的問題，v7.1.x 又修了 `agent.query()` 被 HTTP verb 覆蓋的 bug，使用 agent 請確保版本符合 `migration-pin-safe-version`。
- 若是 token-based（JWT）而非 cookie session，改用 `request-set-auth` 的寫法更直接。
