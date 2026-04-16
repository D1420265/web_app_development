"""
auth.py — 處理登入、註冊與登出的路由 (Controller)
"""
from flask import Blueprint

bp = Blueprint('auth', __name__, url_prefix='/auth')

# TODO: 步驟三實作路由邏輯
# GET/POST /auth/register — 註冊帳號
# GET/POST /auth/login    — 登入系統
# GET      /auth/logout   — 登出系統
