"""
ingredient.py — 食材 (Ingredient) 資料模型

對應資料表: ingredients
欄位: id, name, created_at

提供食材的 CRUD 操作，以及依名稱查詢、依食譜查詢等輔助函式。
食材與食譜之間的多對多關聯由 recipe_ingredients 關聯表管理。
"""
from .db import get_db_connection


def create(data):
    """
    新增一筆食材。

    Args:
        data (dict): 食材資料，必須包含以下鍵值：
            - name (str): 食材名稱（唯一值）

    Returns:
        int | None: 新建食材的 ID；若失敗則回傳 None。
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO ingredients (name) VALUES (?)',
            (data['name'],)
        )
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Error creating ingredient: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_all():
    """
    取得所有食材（依名稱排序）。

    Returns:
        list[dict]: 食材資料的字典列表；若失敗則回傳空列表。
    """
    conn = None
    try:
        conn = get_db_connection()
        ingredients = conn.execute(
            'SELECT * FROM ingredients ORDER BY name'
        ).fetchall()
        return [dict(i) for i in ingredients]
    except Exception as e:
        print(f"Error fetching ingredients: {e}")
        return []
    finally:
        if conn:
            conn.close()


def get_by_id(ingredient_id):
    """
    依 ID 取得單一食材。

    Args:
        ingredient_id (int): 食材 ID。

    Returns:
        dict | None: 食材資料字典；若找不到或失敗則回傳 None。
    """
    conn = None
    try:
        conn = get_db_connection()
        ingredient = conn.execute(
            'SELECT * FROM ingredients WHERE id = ?', (ingredient_id,)
        ).fetchone()
        return dict(ingredient) if ingredient else None
    except Exception as e:
        print(f"Error fetching ingredient: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_by_name(name):
    """
    依名稱取得食材。

    Args:
        name (str): 食材名稱。

    Returns:
        dict | None: 食材資料字典；若找不到或失敗則回傳 None。
    """
    conn = None
    try:
        conn = get_db_connection()
        ingredient = conn.execute(
            'SELECT * FROM ingredients WHERE name = ?', (name,)
        ).fetchone()
        return dict(ingredient) if ingredient else None
    except Exception as e:
        print(f"Error fetching ingredient by name: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_or_create(name):
    """
    依名稱查找食材；若不存在則自動建立。

    此函式在建立食譜時特別有用，可簡化食材的重複檢查邏輯。

    Args:
        name (str): 食材名稱。

    Returns:
        dict | None: 食材資料字典（含 id 與 name）；若失敗則回傳 None。
    """
    conn = None
    try:
        conn = get_db_connection()
        ingredient = conn.execute(
            'SELECT * FROM ingredients WHERE name = ?', (name,)
        ).fetchone()
        if ingredient:
            return dict(ingredient)

        # 不存在，建立新食材
        cursor = conn.cursor()
        cursor.execute('INSERT INTO ingredients (name) VALUES (?)', (name,))
        conn.commit()
        return {'id': cursor.lastrowid, 'name': name}
    except Exception as e:
        print(f"Error in get_or_create ingredient: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_by_recipe_id(recipe_id):
    """
    取得特定食譜的所有食材（透過 recipe_ingredients 關聯表）。

    Args:
        recipe_id (int): 食譜 ID。

    Returns:
        list[dict]: 該食譜的食材列表；若失敗則回傳空列表。
    """
    conn = None
    try:
        conn = get_db_connection()
        ingredients = conn.execute(
            '''SELECT i.id, i.name, i.created_at
               FROM ingredients i
               JOIN recipe_ingredients ri ON i.id = ri.ingredient_id
               WHERE ri.recipe_id = ?
               ORDER BY i.name''',
            (recipe_id,)
        ).fetchall()
        return [dict(i) for i in ingredients]
    except Exception as e:
        print(f"Error fetching ingredients by recipe: {e}")
        return []
    finally:
        if conn:
            conn.close()


def update(ingredient_id, data):
    """
    更新食材名稱。

    Args:
        ingredient_id (int): 要更新的食材 ID。
        data (dict): 要更新的欄位，必須包含：
            - name (str): 新的食材名稱

    Returns:
        bool: 更新成功回傳 True；失敗回傳 False。
    """
    conn = None
    try:
        conn = get_db_connection()
        conn.execute(
            'UPDATE ingredients SET name = ? WHERE id = ?',
            (data['name'], ingredient_id)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating ingredient: {e}")
        return False
    finally:
        if conn:
            conn.close()


def delete(ingredient_id):
    """
    刪除食材（關聯表 recipe_ingredients 會因 ON DELETE CASCADE 自動清除）。

    Args:
        ingredient_id (int): 要刪除的食材 ID。

    Returns:
        bool: 刪除成功回傳 True；失敗回傳 False。
    """
    conn = None
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM ingredients WHERE id = ?', (ingredient_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting ingredient: {e}")
        return False
    finally:
        if conn:
            conn.close()
