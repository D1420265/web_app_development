"""
admin.py — 管理員後台相關邏輯的路由 (Controller)
"""
from flask import Blueprint

bp = Blueprint('admin', __name__, url_prefix='/admin')

# TODO: 步驟三實作路由邏輯
# GET      /admin          — 管理員後台總覽
# GET/POST /admin/recipes  — 管理所有食譜（可刪除）
# GET/POST /admin/users    — 管理所有使用者
