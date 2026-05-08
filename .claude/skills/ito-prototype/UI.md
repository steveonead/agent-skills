# UI Prototype

在同一個 route 上生成**幾個結構截然不同的 UI variant**，可從浮動在底部的 switcher bar 切換。使用者在瀏覽器裡翻閱這些 variant，選一個（或從不同 variant 各取一部分），其餘的丟掉。

若問題是關於邏輯或狀態，選錯分支了，改用 `LOGIC.md`。

## 適用情境

- 「這個頁面應該長什麼樣子？」
- 「我想在提交前先看幾個 dashboard 的設計方向。」
- 「幫 settings 頁面試幾個不同的版面配置。」
- 任何使用者原本要在腦中憑空想像幾個 mockup 來比較的情境。

## 兩個子形狀，強烈建議優先選 A

UI prototype 要有判斷價值，需要和真實的 app 環境並排，包括真實的 header、sidebar、資料和視覺密度。單獨存在的 throwaway route 是真空狀態，每個 variant 在裡面都看起來不錯。只要有合理的既有頁面可以掛載，就預設選 A。

### 子形狀 A：掛載在既有頁面（優先）

Route 已存在。Variant 渲染在**同一個 route**，用 `?variant=` URL 參數切換。既有的資料抓取、params 和 auth 全部保留，只換渲染的子樹。

若 prototype 的對象是尚未有頁面的功能，但它自然會屬於某個頁面（dashboard 的新區塊、settings 的新卡片、既有流程的新步驟），仍屬於子形狀 A，把 variant 掛進宿主頁面就好。

### 子形狀 B：建立新頁面（最後手段）

只有在 prototype 的對象真的沒有任何既有頁面可以寄放時才選，例如全新的頂層 surface，或無法嵌入任何現有流程的功能。

依專案既有的 routing 慣例建立 throwaway route，命名要包含 `prototype` 讓讀者一眼看出是暫時的。同樣用 `?variant=` 切換。

選子形狀 B 之前先確認：真的沒有任何現有頁面可以嵌入嗎？空的 route 會隱藏設計問題，有真實內容的 route 才會暴露問題。

## 流程

### 步驟 1：確認問題與 variant 數量

預設生成 **3 個 variant**，超過 5 個就不再是截然不同的設計方向，只是噪音。

在 prototype 頂端的註解寫一行計畫：

> 「三個 settings 頁面的 variant，用 `?variant=` 切換，掛在既有 `/settings` route 上。」

不管使用者在不在線，這一行都要有。

### 步驟 2：生成結構截然不同的 variant

草擬每個 variant，遵守：

- 頁面的用途與可取用的資料範圍。
- 專案的 component library 與樣式系統（shadcn/ui + Tailwind）。
- 清楚的 export 名稱，例如 `VariantA`、`VariantB`、`VariantC`。

Variant 必須在**結構上有差異**，不同的版面配置、不同的資訊層次、不同的主要互動入口，不只是換顏色或文案。若兩個草稿出來太像，重做其中一個，給自己加上明確限制（例如「這個不能用 card grid」）。

### 步驟 3：接線

在 route 上建立一個 switcher 元件：

```tsx
// 虛擬碼，依框架調整（Next.js App Router / Pages Router / React Router 等）
const variant = searchParams.get('variant') ?? 'A';
return (
  <>
    {variant === 'A' && <VariantA {...data} />}
    {variant === 'B' && <VariantB {...data} />}
    {variant === 'C' && <VariantC {...data} />}
    <PrototypeSwitcher variants={['A', 'B', 'C']} current={variant} />
  </>
);
```

子形狀 A：保留所有既有的資料抓取，只換渲染的子樹。
子形狀 B：throwaway route 掛載同樣的 switcher。

### 步驟 4：建立浮動 switcher bar

固定在畫面底部中央，三個元素：

- **左箭頭**：切換到上一個 variant（循環）。
- **Variant 標籤**：顯示當前的 variant key，若有名稱一起顯示，例如「B — Sidebar layout」。
- **右箭頭**：往下一個切換（循環）。

行為規格：
- 點箭頭時更新 URL 的 search param（用框架提供的 router，例如 Next.js 的 `router.replace`），讓 variant 可以分享，且 reload 後狀態保留。
- 鍵盤 `←` `→` 方向鍵同樣可以切換。`<input>`、`<textarea>` 或 `[contenteditable]` 被 focus 時不攔截方向鍵。
- 外觀要明顯和頁面設計區隔（例如高對比的 pill 搭配 shadow），讓人一眼看出這不是設計的一部分。
- **在 production 環境隱藏**：用 `process.env.NODE_ENV !== 'production'` 控制，防止誤 merge 時 switcher 帶上線。

把 switcher 做成一個共用元件，子形狀 A 和 B 都可以複用。

### 步驟 5：把操作權交給使用者

提供 URL 和各 `?variant=` 的 key，讓使用者自己去翻。通常最有價值的回饋是「我想要 B 的 header 配上 C 的 sidebar」，那才是使用者真正想要的設計。

### 步驟 6：記錄答案，清理現場

確定哪個 variant 勝出後，記錄選了哪個以及原因（commit message、ADR、issue，或若使用者不在線先放在 `NOTES.md`）。

然後清理：

- **子形狀 A**：刪掉落敗的 variant 元件和 switcher，把勝出的 variant 整合進既有頁面。
- **子形狀 B**：把勝出的 variant 升格為正式 route，刪掉 throwaway route 和 switcher。

Variant 元件和 switcher 腐爛得很快，不要留著。

## Anti-patterns

- **Variant 只差顏色或文案。** 那是微調，不是 prototype。真正的 variant 要在結構和資訊架構上有根本的不同。
- **Variant 之間共用太多程式碼。** 共用 `<Header>` 沒問題，共用 `<Layout>` 就失去意義了，每個 variant 要能自由選擇自己的版面。
- **讓 variant 接上真正的 mutation。** 問題是「長什麼樣」，不是「後端有沒有在動」，指向 stub 就夠了。
- **直接把 prototype 升格成正式程式碼。** Variant 是在 prototype 條件下寫的（沒有測試、最低限度的錯誤處理），進正式程式碼之前要重新寫一次。
