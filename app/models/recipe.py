"""
recipe.py — 食譜 (Recipe) 資料模型

對應資料表: recipes
欄位: id, user_id, title, portions, steps, created_at, updated_at

提供食譜的 CRUD 操作，以及關鍵字搜尋、依使用者篩選、
食材組合搜尋等核心功能。食譜與食材之間的多對多關聯
透過 recipe_ingredients 關聯表管理。
"""
from .db import get_db_connection


def create(data):
    """
    新增一筆食譜，並建立與食材的多對多關聯。

    Args:
        data (dict): 食譜資料，必須包含以下鍵值：
            - user_id (int): 建立者的使用者 ID
            - title (str): 食譜標題
            - steps (str): 料理步驟
            - portions (int, optional): 份量人數
            - ingredients (list[str], optional): 食材名稱列表

    Returns:
        int | None: 新建食譜的 ID；若失敗則回傳 None。
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO recipes (user_id, title, portions, steps) VALUES (?, ?, ?, ?)',
            (data['user_id'], data['title'], data.get('portions'), data['steps'])
        )
        recipe_id = cursor.lastrowid

        # 處理食材的多對多關聯
        ingredients = data.get('ingredients', [])
        for ingredient_name in ingredients:
            ingredient_name = ingredient_name.strip()
            if not ingredient_name:
                continue
            # 查找或建立食材
            existing = cursor.execute(
                'SELECT id FROM ingredients WHERE name = ?', (ingredient_name,)
            ).fetchone()
            if existing:
                ingredient_id = existing['id']
            else:
                cursor.execute(
                    'INSERT INTO ingredients (name) VALUES (?)', (ingredient_name,)
                )
                ingredient_id = cursor.lastrowid
            # 建立關聯
            cursor.execute(
                'INSERT OR IGNORE INTO recipe_ingredients (recipe_id, ingredient_id) VALUES (?, ?)',
                (recipe_id, ingredient_id)
            )

        conn.commit()
        return recipe_id
    except Exception as e:
        print(f"Error creating recipe: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()


def get_all():
    """
    取得所有食譜（按建立時間由新到舊排序）。

    Returns:
        list[dict]: 食譜資料的字典列表；若失敗則回傳空列表。
    """
    conn = None
    try:
        conn = get_db_connection()
        recipes = conn.execute(
            'SELECT * FROM recipes ORDER BY created_at DESC'
        ).fetchall()
        return [dict(r) for r in recipes]
    except Exception as e:
        print(f"Error fetching recipes: {e}")
        return []
    finally:
        if conn:
            conn.close()


def get_by_id(recipe_id):
    """
    依 ID 取得單一食譜（含該食譜的所有食材）。

    Args:
        recipe_id (int): 食譜 ID。

    Returns:
        dict | None: 食譜資料字典，額外包含 'ingredients' 鍵
                     （食材字典列表）；若找不到或失敗則回傳 None。
    """
    conn = None
    try:
        conn = get_db_connection()
        recipe = conn.execute(
            'SELECT * FROM recipes WHERE id = ?', (recipe_id,)
        ).fetchone()
        if not recipe:
            return None

        result = dict(recipe)

        # 取得該食譜的所有食材
        ingredients = conn.execute(
            '''SELECT i.id, i.name
               FROM ingredients i
               JOIN recipe_ingredients ri ON i.id = ri.ingredient_id
               WHERE ri.recipe_id = ?
               ORDER BY i.name''',
            (recipe_id,)
        ).fetchall()
        result['ingredients'] = [dict(ing) for ing in ingredients]

        return result
    except Exception as e:
        print(f"Error fetching recipe: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_by_user_id(user_id):
    """
    取得特定使用者建立的所有食譜（用於「我的收藏」頁面）。

    Args:
        user_id (int): 使用者 ID。

    Returns:
        list[dict]: 該使用者的食譜列表；若失敗則回傳空列表。
    """
    conn = None
    try:
        conn = get_db_connection()
        recipes = conn.execute(
            'SELECT * FROM recipes WHERE user_id = ? ORDER BY created_at DESC',
            (user_id,)
        ).fetchall()
        return [dict(r) for r in recipes]
    except Exception as e:
        print(f"Error fetching recipes by user: {e}")
        return []
    finally:
        if conn:
            conn.close()


def search(keyword):
    """
    依關鍵字搜尋食譜（比對標題與步驟內容）。

    Args:
        keyword (str): 搜尋關鍵字。

    Returns:
        list[dict]: 符合條件的食譜列表；若失敗則回傳空列表。
    """
    conn = None
    try:
        conn = get_db_connection()
        like_pattern = f'%{keyword}%'
        recipes = conn.execute(
            '''SELECT * FROM recipes
               WHERE title LIKE ? OR steps LIKE ?
               ORDER BY created_at DESC''',
            (like_pattern, like_pattern)
        ).fetchall()
        return [dict(r) for r in recipes]
    except Exception as e:
        print(f"Error searching recipes: {e}")
        return []
    finally:
        if conn:
            conn.close()


def search_by_ingredients(ingredient_names):
    """
    依食材組合搜尋食譜——找出包含任一指定食材的食譜，
    並依「匹配食材數量」由多到少排序（核心推薦功能）。

    Args:
        ingredient_names (list[str]): 使用者手邊現有的食材名稱列表。

    Returns:
        list[dict]: 食譜列表，每筆額外包含 'matched_count'（匹配食材數）
                     與 'matched_ingredients'（匹配的食材名稱，逗號分隔）；
                     若失敗則回傳空列表。
    """
    conn = None
    try:
        conn = get_db_connection()
        # 清理食材名稱
        cleaned = [name.strip() for name in ingredient_names if name.strip()]
        if not cleaned:
            return []

        # 使用動態佔位符
        placeholders = ','.join('?' for _ in cleaned)
        recipes = conn.execute(
            f'''SELECT r.*, COUNT(ri.ingredient_id) AS matched_count,
                       GROUP_CONCAT(i.name, ', ') AS matched_ingredients
                FROM recipes r
                JOIN recipe_ingredients ri ON r.id = ri.recipe_id
                JOIN ingredients i ON ri.ingredient_id = i.id
                WHERE i.name IN ({placeholders})
                GROUP BY r.id
                ORDER BY matched_count DESC, r.created_at DESC''',
            cleaned
        ).fetchall()
        return [dict(r) for r in recipes]
    except Exception as e:
        print(f"Error searching recipes by ingredients: {e}")
        return []
    finally:
        if conn:
            conn.close()


def update(recipe_id, data):
    """
    更新食譜資料，並重新建立食材關聯。

    Args:
        recipe_id (int): 要更新的食譜 ID。
        data (dict): 要更新的欄位，可包含：
            - title (str): 食譜標題
            - portions (int, optional): 份量人數
            - steps (str): 料理步驟
            - ingredients (list[str], optional): 食材名稱列表

    Returns:
        bool: 更新成功回傳 True；失敗回傳 False。
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''UPDATE recipes
               SET title = ?, portions = ?, steps = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?''',
            (data['title'], data.get('portions'), data['steps'], recipe_id)
        )

        # 若有提供食材列表，重新建立關聯
        if 'ingredients' in data:
            # 先移除舊的關聯
            cursor.execute(
                'DELETE FROM recipe_ingredients WHERE recipe_id = ?', (recipe_id,)
            )
            # 建立新的關聯
            for ingredient_name in data['ingredients']:
                ingredient_name = ingredient_name.strip()
                if not ingredient_name:
                    continue
                existing = cursor.execute(
                    'SELECT id FROM ingredients WHERE name = ?', (ingredient_name,)
                ).fetchone()
                if existing:
                    ingredient_id = existing['id']
                else:
                    cursor.execute(
                        'INSERT INTO ingredients (name) VALUES (?)', (ingredient_name,)
                    )
                    ingredient_id = cursor.lastrowid
                cursor.execute(
                    'INSERT OR IGNORE INTO recipe_ingredients (recipe_id, ingredient_id) VALUES (?, ?)',
                    (recipe_id, ingredient_id)
                )

        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating recipe: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def delete(recipe_id):
    """
    刪除食譜（關聯表 recipe_ingredients 會因 ON DELETE CASCADE 自動清除）。

    Args:
        recipe_id (int): 要刪除的食譜 ID。

    Returns:
        bool: 刪除成功回傳 True；失敗回傳 False。
    """
    conn = None
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM recipes WHERE id = ?', (recipe_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting recipe: {e}")
        return False
    finally:
        if conn:
            conn.close()
