# 系統架構設計 (Architecture) - 食譜收藏夾系統

## 1. 技術架構說明

本專案將採用經典的伺服器端渲染 (Server-Side Rendering, SSR) 的方式開發。由於專案為從零開始的 MVP，採用一體化 (Monolithic) 的設計能加快開發速度，並且足以支撐初期的流量與功能需求。

### 選用技術與原因
- **後端框架：Python + Flask**
  - **原因**：Flask 是輕量級且高擴展性的微框架，十分適合開發中小型網站或 MVP，讓開發者能以最少的程式碼快速建構。
- **模板引擎：Jinja2**
  - **原因**：Flask 原生支援 Jinja2，可以方便地在 HTML 中嵌入 Python 語法與邏輯，實現前後端結合的伺服器渲染。
- **資料庫：SQLite (透過 SQLAlchemy)**
  - **原因**：不需要額外安裝或設定獨立的資料庫伺服器，對初學者友好且便於遷移與測試。使用 SQLAlchemy 這個 ORM 工具可以避免手寫繁瑣的 SQL 語句。
- **前端：HTML/CSS (可搭輕量框架如 Tailwind / Bootstrap)**
  - **原因**：不進行前後端分離，降低多專案維護及 API 設計的複雜度。

### Flask MVC 模式說明
雖然 Flask 本身沒有強制的架構規範，但我們會採用類似 MVC (Model-View-Controller) 的概念來組織程式碼：
- **Model (模型)**：負責與 SQLite 資料庫互動，定義資料表結構（如用戶、食譜、食材等），處理資料的新增、修改、刪除與查詢（由 SQLAlchemy 處理）。
- **View (視圖)**：負責將資料渲染成網頁，也就是 Jinja2 模板（`.html` 檔）處理的範圍。
- **Controller (控制器)**：在 Flask 裡負責「路由 (Routes)」。接收使用者的網頁請求、呼叫 Model 取得或寫入資料，最後將資料傳遞給 View 進行渲染。

---

## 2. 專案資料夾結構

為了讓程式碼清晰好管理，避免所有功能都塞在同一個檔案內，我們設計如下的模組化資料夾結構：

```text
web_app_development/
├── app/                      ← 應用程式的主要程式碼放在此資料夾內
│   ├── __init__.py           ← 用來初始化 Flask 應用、資料庫與所有設定
│   ├── models/               ← (Model) 資料庫模型
│   │   ├── __init__.py
│   │   ├── user.py           ← 使用者資料模型
│   │   ├── recipe.py         ← 食譜資料模型
│   │   └── ingredient.py     ← 食材與關聯模型
│   ├── routes/               ← (Controller) 路由邏輯，處理 HTTP 請求
│   │   ├── __init__.py
│   │   ├── auth.py           ← 處理登入、註冊與登出
│   │   ├── main.py           ← 首頁與搜尋頁面
│   │   ├── recipe.py         ← 處理食譜 CRUD (建立/編輯/刪除)
│   │   └── admin.py          ← 管理員後台相關邏輯
│   ├── templates/            ← (View) Jinja2 HTML 模板
│   │   ├── base.html         ← 共用版型（含導覽列與頁尾）
│   │   ├── index.html        ← 首頁
│   │   ├── auth/             ← 認證相關頁面（login.html, register.html）
│   │   └── recipes/          ← 食譜相關頁面（list.html, detail.html, form.html）
│   └── static/               ← 靜態資源檔案
│       ├── css/
│       │   └── style.css     ← 自訂樣式表
│       ├── js/
│       │   └── main.js       ← 自訂 JavaScript
│       └── images/           ← 網站圖片、食譜預設縮圖
├── instance/                 ← 放置會變動或機密的執行實例資料（如本機測試的 DB 或設定）
│   └── database.db           ← SQLite 資料庫儲存檔
├── docs/                     ← 專案文件存放區
│   ├── PRD.md                ← 產品需求文件
│   └── ARCHITECTURE.md       ← 系統架構設計 (本文件)
├── requirements.txt          ← 記錄專案所有依賴的 Python 套件
└── app.py                    ← 專案入口點，負責啟動 Flask 伺服器
```

---

## 3. 元件關係圖

以下展示各元件之間如何分工運作：

```mermaid
flowchart TD
    Browser((使用者瀏覽器))
    
    subgraph 伺服器端
        Route[Flask Routes\n(Controller)]
        Model[SQLAlchemy Models\n(Model)]
        Template[Jinja2 Templates\n(View)]
    end
    
    DB[(SQLite 資料庫)]

    Browser -- "1. 送出 HTTP Request\n(如找食譜 /search)" --> Route
    Route -- "2. 查詢食譜資料" --> Model
    Model -- "3. 讀寫操作" --> DB
    DB -- "4. 回傳資料" --> Model
    Model -- "5. 傳送資料物件" --> Route
    Route -- "6. 將資料傳入模板" --> Template
    Template -- "7. 渲染出完整 HTML" --> Route
    Route -- "8. 回傳 HTTP Response" --> Browser
```

---

## 4. 關鍵設計決策

1. **採用藍圖 (Blueprints) 切分路由**
   - **問題**：隨著食譜、使用者認證、管理員等功能增加，將所有路由寫在同一個檔案會難以維護。
   - **決策**：在 `routes/` 目錄利用 Flask Blueprint 機制把功能模組化（如分拆 `auth.py`, `recipe.py`, `admin.py`），並在 `app/__init__.py` 中統一註冊。
   - **好處**：職責分明，開發時可以同時分工，未來擴充也更容易。

2. **選擇使用 SQLAlchemy ORM**
   - **問題**：直接撰寫原生的 SQL 語法容易因為字串拼接出錯或造成 SQL Injection，同時可維護性較低。
   - **決策**：引進 SQLAlchemy 這個進階的 ORM（物件關聯映射），讓開發者可以直接用 Python 的「類別 (Class)」與「物件 (Object)」來操作資料庫。
   - **好處**：提升程式安全性且易於除錯，後續若需更換至 PostgreSQL 也能無縫切換。

3. **實作食材「多對多 (Many-to-Many)」關聯**
   - **問題**：每個食譜包含多種食材，每種食材也出現在多個食譜中。
   - **決策**：在資料庫設計時加入關聯表 (Association Table) 來串聯 `Recipe` (食譜) 與 `Ingredient` (食材)。
   - **好處**：使得「從食材組合搜尋食譜」這項核心功能可以用高效的資料庫關聯查詢實現，而不是回傳所有資料在伺服器端比對。

4. **採用繼承機制的 Jinja2 模板**
   - **問題**：每個頁面都會有重複的導覽列與頁尾，若每個檔案都寫一次非常累贅。
    - **決策**：設計一個母板 `base.html` 包含共同版面結構，其他頁面透過 `extends 'base.html'` 語法來繼承與展開。
   - **好處**：只要改一個地方，所有頁面都能更動。
