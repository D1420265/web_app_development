"""
user.py — 使用者 (User) 資料模型

對應資料表: users
欄位: id, username, email, password_hash, created_at

提供使用者的 CRUD 操作以及依 email / username 查詢的輔助函式。
"""
from .db import get_db_connection


def create(data):
    """
    新增一名使用者。

    Args:
        data (dict): 使用者資料，必須包含以下鍵值：
            - username (str): 使用者名稱
            - email (str): 電子郵件（唯一值）
            - password_hash (str): 密碼雜湊值

    Returns:
        int | None: 新建使用者的 ID；若失敗則回傳 None。
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            (data['username'], data['email'], data['password_hash'])
        )
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Error creating user: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_all():
    """
    取得所有使用者。

    Returns:
        list[dict]: 使用者資料的字典列表；若失敗則回傳空列表。
    """
    conn = None
    try:
        conn = get_db_connection()
        users = conn.execute(
            'SELECT * FROM users ORDER BY created_at DESC'
        ).fetchall()
        return [dict(u) for u in users]
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []
    finally:
        if conn:
            conn.close()


def get_by_id(user_id):
    """
    依 ID 取得單一使用者。

    Args:
        user_id (int): 使用者 ID。

    Returns:
        dict | None: 使用者資料字典；若找不到或失敗則回傳 None。
    """
    conn = None
    try:
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()
        return dict(user) if user else None
    except Exception as e:
        print(f"Error fetching user by id: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_by_email(email):
    """
    依電子郵件取得使用者（用於登入驗證）。

    Args:
        email (str): 電子郵件地址。

    Returns:
        dict | None: 使用者資料字典；若找不到或失敗則回傳 None。
    """
    conn = None
    try:
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE email = ?', (email,)
        ).fetchone()
        return dict(user) if user else None
    except Exception as e:
        print(f"Error fetching user by email: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_by_username(username):
    """
    依使用者名稱取得使用者。

    Args:
        username (str): 使用者名稱。

    Returns:
        dict | None: 使用者資料字典；若找不到或失敗則回傳 None。
    """
    conn = None
    try:
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()
        return dict(user) if user else None
    except Exception as e:
        print(f"Error fetching user by username: {e}")
        return None
    finally:
        if conn:
            conn.close()


def update(user_id, data):
    """
    更新使用者資料。

    Args:
        user_id (int): 要更新的使用者 ID。
        data (dict): 要更新的欄位，可包含：
            - username (str): 使用者名稱
            - email (str): 電子郵件
            - password_hash (str): 密碼雜湊值

    Returns:
        bool: 更新成功回傳 True；失敗回傳 False。
    """
    conn = None
    try:
        conn = get_db_connection()
        conn.execute(
            'UPDATE users SET username = ?, email = ?, password_hash = ? WHERE id = ?',
            (data['username'], data['email'], data['password_hash'], user_id)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating user: {e}")
        return False
    finally:
        if conn:
            conn.close()


def delete(user_id):
    """
    刪除使用者。

    Args:
        user_id (int): 要刪除的使用者 ID。

    Returns:
        bool: 刪除成功回傳 True；失敗回傳 False。
    """
    conn = None
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False
    finally:
        if conn:
            conn.close()
