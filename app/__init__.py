from flask import Flask
import os


def create_app():
    """建立並設定 Flask 應用程式實例。"""
    app = Flask(__name__)

    # 載入設定
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-12345')

    # 確保 instance 資料夾存在（用於存放 SQLite 資料庫）
    os.makedirs(app.instance_path, exist_ok=True)

    with app.app_context():
        # 註冊 Blueprints（依照 ARCHITECTURE.md 的路由模組）
        from .routes import main, recipe, auth, admin

        app.register_blueprint(main.bp)       # 首頁與搜尋
        app.register_blueprint(recipe.bp)     # 食譜 CRUD
        app.register_blueprint(auth.bp)       # 登入、註冊、登出
        app.register_blueprint(admin.bp)      # 管理員後台

    return app


def init_db():
    """初始化資料庫（執行 database/schema.sql）。"""
    from .models.db import init_db as initialize_database
    initialize_database()
