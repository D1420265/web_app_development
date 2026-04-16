"""
db.py — 資料庫連線與初始化工具模組

提供所有 Model 共用的資料庫連線函式，以及資料庫初始化功能。
資料庫檔案儲存於 instance/database.db。
"""
import sqlite3
import os


def get_db_connection():
    """
    建立並回傳一個 SQLite 資料庫連線。

    Returns:
        sqlite3.Connection: 已設定 row_factory 的資料庫連線物件。

    說明:
        - 自動確保 instance/ 目錄存在
        - 設定 row_factory = sqlite3.Row，讓查詢結果可用欄位名稱取值
        - 啟用外鍵約束 (PRAGMA foreign_keys)，確保 ON DELETE CASCADE 等行為正常運作
    """
    # 確保 instance 目錄存在
    os.makedirs('instance', exist_ok=True)
    db_path = os.path.join('instance', 'database.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    # 啟用外鍵約束（SQLite 預設關閉，必須每次連線都開啟）
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def init_db():
    """
    初始化資料庫——執行 database/schema.sql 建立所有資料表。

    此函式會讀取 SQL 檔案並一次性執行所有 CREATE TABLE 語句。
    並確保建立一個預設使用者 (用於本地測試，避免外鍵限制報錯)。
    """
    conn = get_db_connection()
    try:
        with open('database/schema.sql', 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        
        # 確保存在預設的 Local User (ID 會自動給 1 如果是全空的 DB)
        # 用 INSERT OR IGNORE 防止重複執行時報錯
        conn.execute('''
            INSERT OR IGNORE INTO users (id, username, email, password_hash)
            VALUES (1, 'LocalUser', 'local@example.com', 'test_hash_only')
        ''')
        
        conn.commit()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing DB: {e}")
    finally:
        conn.close()
