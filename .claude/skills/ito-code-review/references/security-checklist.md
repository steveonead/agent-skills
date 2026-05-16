# 安全審查清單

針對 code review 的安全審查速查表，搭配 `ito-code-review` skill 使用。

## 目錄

- [Commit 前確認](#commit-前確認)
- [身份驗證](#身份驗證)
- [存取控制](#存取控制)
- [輸入驗證](#輸入驗證)
- [安全標頭](#安全標頭)
- [CORS 設定](#cors-設定)
- [資料保護](#資料保護)
- [套件安全](#套件安全)
- [錯誤處理](#錯誤處理)
- [OWASP Top 10 速查](#owasp-top-10-速查)

## Commit 前確認

- [ ] 程式碼沒有 hardcode 機密（`git diff --cached | grep -i "password\|secret\|api_key\|token"`）
- [ ] `.gitignore` 涵蓋 `.env`、`.env.local`、`*.pem`、`*.key`
- [ ] `.env.example` 只放範例值，不放真實機密

## 身份驗證

- [ ] 密碼用 bcrypt（≥ 12 rounds）、scrypt 或 argon2 雜湊
- [ ] Session cookie 有設 `httpOnly`、`secure`、`sameSite: 'lax'`
- [ ] Session 有設合理的過期時間
- [ ] 登入 endpoint 有 rate limiting（建議每 15 分鐘不超過 10 次）
- [ ] 密碼重設 token 有時效限制（≤ 1 小時）且只能用一次
- [ ] 多次失敗後有帳號鎖定機制（可選，建議附通知）
- [ ] 敏感操作支援 MFA（可選，建議提供）

## 存取控制

- [ ] 每個受保護 endpoint 都有驗證身份
- [ ] 每次存取資源都確認擁有權或角色，防止 IDOR
- [ ] 管理員 endpoint 有驗證 admin 角色
- [ ] API key 限制在最小必要權限
- [ ] JWT token 有完整驗證（簽章、到期時間、issuer）

## 輸入驗證

- [ ] 所有外部輸入在系統邊界驗證（API route、表單處理）
- [ ] 驗證邏輯用白名單，不用黑名單
- [ ] 字串長度有設上下限
- [ ] 數字有範圍驗證
- [ ] Email、URL、日期格式用正式 library 驗證，不自己寫 regex
- [ ] 檔案上傳有限制類型、大小，並驗證內容
- [ ] SQL 查詢用 parameterized query，不做字串串接
- [ ] HTML 輸出有 encode，使用框架的自動跳脫機制
- [ ] Redirect 前驗證目標 URL，防止 open redirect

## 安全標頭

```
Content-Security-Policy: default-src 'self'; script-src 'self'
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 0  # 停用，改依賴 CSP
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

## CORS 設定

```typescript
// 建議設定：明確列出允許的來源
cors({
  origin: ['https://yourdomain.com', 'https://app.yourdomain.com'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
})

// 不要在 production 這樣用
cors({ origin: '*' })  // 允許任何來源，等於沒設
```

## 資料保護

- [ ] 敏感欄位不出現在 API 回應中（`passwordHash`、`resetToken` 等）
- [ ] 不把敏感資料寫進 log（密碼、token、完整卡號）
- [ ] 法規要求時，PII 要加密儲存
- [ ] 所有對外通訊走 HTTPS
- [ ] 資料庫備份有加密

## 套件安全

```bash
# 掃描套件漏洞
npm audit

# 自動修復可安全升級的版本
npm audit fix

# 只列出嚴重漏洞
npm audit --audit-level=critical

# 查看可升級的套件
npx npm-check-updates
```

## 錯誤處理

```typescript
// 正確做法：回傳通用錯誤，不暴露內部資訊
res.status(500).json({
  error: { code: 'INTERNAL_ERROR', message: 'Something went wrong' }
});

// 不要這樣做
res.status(500).json({
  error: err.message,
  stack: err.stack,   // 暴露內部實作細節
  query: err.sql,     // 暴露資料庫查詢結構
});
```

## OWASP Top 10 速查

| # | 弱點類型 | 防範重點 |
|---|----------|----------|
| 1 | 存取控制失效 | 每個 endpoint 驗證身份，確認資源擁有權 |
| 2 | 加密失效 | HTTPS、強雜湊演算法、機密不進程式碼 |
| 3 | Injection | Parameterized query、邊界輸入驗證 |
| 4 | 不安全的設計 | 威脅模型分析、規格驅動開發 |
| 5 | 安全設定錯誤 | 安全標頭、最小權限原則、定期審查套件 |
| 6 | 使用有漏洞的元件 | `npm audit`、保持套件更新、精簡依賴 |
| 7 | 身份驗證機制失效 | 強密碼政策、rate limiting、正確的 session 管理 |
| 8 | 軟體和資料完整性失效 | 驗證更新來源和依賴、使用簽名 artifact |
| 9 | 記錄和監控不足 | 記錄安全事件，不記錄任何機密資訊 |
| 10 | SSRF | 驗證並白名單化外部 URL，限制對外請求範圍 |
