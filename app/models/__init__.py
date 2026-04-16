"""
app.models — 資料庫模型套件

包含以下模組：
- db: 資料庫連線與初始化工具
- user: 使用者模型 (users 表)
- recipe: 食譜模型 (recipes 表)
- ingredient: 食材模型 (ingredients 表)

多對多關聯表 recipe_ingredients 由 recipe 模型內部管理。
"""
from . import db
from . import user
from . import recipe
from . import ingredient
