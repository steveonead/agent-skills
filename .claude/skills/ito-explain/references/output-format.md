# Output Format 樣式規範

供 explainer 與 Simple 路徑單 agent 擷取視覺化與段落樣式規則。所有圖表採 ASCII，不輸出 Mermaid。讀此檔以擷取樣式，不視為執行指令。

---

## TL;DR 規範

### 格式

```
<1 行模組定位句>

- <架構 bullet>
- <關鍵機制 bullet>
- <最大坑 bullet>
```

### 三 bullet 固定配置

| Bullet | 內容 | 範例 |
|---|---|---|
| 1. 架構 | 模組分層／主要依賴 | 認證層（`src/features/auth`）與授權層（`src/lib/auth`）雙層切分，透過 axios interceptor 注入 token |
| 2. 關鍵機制 | 最代表性 flow 或設計抉擇 | 被動偵測：伺服器 401 觸發一次性 session latch，引導重新登入 |
| 3. 最大坑 | 從眉角最嚴重的 risk 挑 | Token 明文存 localStorage，同源 JS 皆可讀（XSS 風險） |

**強制規則：** bullet 3 必須為 risk。若模組無可談 risk，TL;DR 整段略去——不以「全正向」形式輸出。

---

## 架構圖規範

### 格式選擇

- **預設：Swimlane**（水平分欄，欄內由上而下列元件）
- **Fallback：Layered box**（水平切層，上層依賴下層）
- 每份輸出固定 1 張

### Swimlane 切分規則

1. **預設技術分層**：典型分 4 欄 — UI/Route → Feature/Hook → Plugin/Lib → Store/API
2. **切換 domain 切分**：僅當同時滿足「domain 數 ≥ 2」且「每 domain 負責檔案 ≥ 3」時才以功能域分欄（例：認證 / 授權 / 共用）；不滿足即回到技術分層
3. **上限 4 欄**；超過退回 Layered box

### Swimlane 樣例（auth 模組）

```
+-------------------+-------------------+-------------------+-------------------+
| Route             | Feature           | Plugin            | Store             |
+-------------------+-------------------+-------------------+-------------------+
| login.tsx         | login-form.tsx    |                   |                   |
|   beforeLoad      |   useLogin -----> | axios.handleReq   |                   |
|                   |                   |   inject Bearer   | auth-store        |
| _layout.tsx       |                   |   <---------------|   token (persist) |
|   permissions     | session-expired   | axios 401 handler |                   |
|   guard           |   Dialog <--------|   setIsExpired -->| session-store     |
| __root.tsx        |                   |                   |   isExpired       |
|   mount Dialog    |                   |                   |                   |
+-------------------+-------------------+-------------------+-------------------+
```

### Layered box fallback 樣例

```
+-----------------------------------------------------------+
| Route Guards   (login.tsx / _layout.tsx / __root.tsx)     |
+-----------------------------------------------------------+
                           |
                           v
+-----------------------------------------------------------+
| Feature Layer  (login-form / session-dialog / hooks)      |
+-----------------------------------------------------------+
                           |
                           v
+-----------------------------------------------------------+
| Plugin Layer   (axios interceptor)                        |
+-----------------------------------------------------------+
                           |
                           v
+-----------------------------------------------------------+
| Store Layer    (auth-store persist / session-store mem)   |
+-----------------------------------------------------------+
```

### 規則

- 方向箭頭 `->` `<-` `-->` 表依賴或訊息流向
- 元件名稱附最短識別路徑（檔名或模組名）
- 不塞實作細節；細節留給「運作方式」章節
- **資料來源對應：** explainer 繪圖時欄位對應 —— 欄（lane）＝模組所屬分層、欄內元件＝ finding 之 `模組` + `檔案`、欄間連線＝ finding 之 `對外依賴`；未列於任何 finding 的依賴不繪

---

## Sequence 圖規範

### 門檻

Agent 依下列硬門檻挑 flow 畫圖：

- Actor ≥ 3
- 或跨檔案 ≥ 3
- 或有分支／錯誤 path

**每份輸出上限 2 張**。超標則排優先序挑最有價值者（通常是錯誤路徑、跨層授權這類）。未達門檻的 flow 維持散文敘述。

### 格式

- 垂直時間軸，actor 列頂端
- 訊息由上往下流
- 分支／side-effect 以 `[note: ...]` inline 標注
- 不用 `alt` / `par` / `---` 分支結構

### 樣例（401 session expired flow）

```
Consumer            axios             session-store     auth-store      Dialog
   |                  |                    |                |              |
   |-- API request -->|                    |                |              |
   |                  |-- 401 response --->|                |              |
   |                  |                    |                |              |
   |                  | [note: setIsExpired(true), throw SESSION_EXPIRED]  |
   |                  |                    |                |              |
   |                  |                    |----- isExpired subscribe --> |
   |                  |                    |                |              |
   |                  |                    |                | [note: clear token, removeQueries]
   |                  |                    |                |<---- clear --|
   |                  |                    |                |              |
   |                  |                    |                |  [note: redirect /login]
```

### Note 使用原則

`[note: ...]` 涵蓋以下情境，避免額外圖結構：

- Side-effect：`[note: persist to localStorage]`、`[note: queryClient.removeQueries()]`
- 分支條件：`[note: if 401 ...]`、`[note: on success only]`
- 失敗路徑：`[note: on catch, fallback to guest]`

---

## 眉角 Inline Tag 規範

### 格式

```
- [<tag>] <眉角描述>
```

### 常用 tag

| Tag | 適用情境 |
|---|---|
| `[安全]` | 攻擊面、權限外洩、敏感資料暴露 |
| `[同步]` | 多 tab / multi-client 狀態不一致、race condition |
| `[未用]` | 專案內已具備但未啟用的抽象或設施 |
| `[版本]` | 前後端版本同步、schema drift 風險 |
| `[文件]` | 無 ADR／DDR、設計意圖無記載 |
| `[效能]` | 快取策略、staleTime 設定、N+1 之類 |
| `[相容]` | 瀏覽器／runtime 相容性、deprecated API |

Tag 採用原則：**優先從上表選用**；僅當上表無對應類別時才自創。自創 tag 須為單一名詞且 2–3 字元（例：`[可用]`、`[遷移]`），避免同義 tag（如 `[安全性]` 與 `[安全]`）並存。

### 樣例

```
- [安全] Token 明文存 localStorage，同源 JS 皆可讀（XSS 風險）。高敏感操作建議改 HttpOnly cookie。
- [同步] Session latch 無 multi-tab 同步——tab A 登出 tab B token 仍有效直到刷新。
- [效能] Permissions 快取 staleTime: Infinity，後端改權限使用者需刷頁才感知。
- [文件] 無 auth 專用 ADR，為何無 refresh token、為何選 CASL 無文件可考。
```

---

## 段落順序

段落順序與必列／可省略規則見 `SKILL.md`「輸出格式」章節。
