"""
main.py — 首頁與搜尋頁面的路由 (Controller)

處理網站首頁、關鍵字搜尋、以及食材組合搜尋（核心推薦功能）。
使用 Flask Blueprint 組織路由。

路由清單：
    GET      /                    — 首頁，列出最新食譜
    GET      /search              — 關鍵字搜尋食譜
    GET/POST /search/ingredients  — 食材組合搜尋（推薦功能）
"""
from flask import Blueprint, render_template, request, flash
from app.models import recipe as recipe_model
from app.models import ingredient as ingredient_model

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """首頁——列出最新的食譜。

    直接從資料庫取得所有食譜（已按建立時間由新到舊排序），
    傳入首頁模板渲染。
    """
    recipes = recipe_model.get_all()
    return render_template('index.html', recipes=recipes)


@bp.route('/search')
def search():
    """關鍵字搜尋食譜。

    從 URL 查詢參數 ?q=... 取得關鍵字，比對食譜標題與步驟內容，
    回傳搜尋結果列表。若未提供關鍵字，顯示空結果。
    """
    keyword = request.args.get('q', '').strip()
    recipes = []

    if keyword:
        recipes = recipe_model.search(keyword)
        if not recipes:
            flash('找不到符合的食譜，請嘗試其他關鍵字。', 'info')

    return render_template('search.html', recipes=recipes, keyword=keyword)


@bp.route('/search/ingredients', methods=('GET', 'POST'))
def search_by_ingredients():
    """食材組合搜尋——核心推薦功能。

    GET  — 顯示食材輸入表單，並列出所有已知食材供參考。
    POST — 接收使用者輸入的食材清單，查詢包含這些食材的食譜，
           依匹配數量由多到少排序。

    使用者可以用逗號或頓號分隔多種食材。
    """
    recipes = []
    ingredients_str = ''
    all_ingredients = ingredient_model.get_all()

    if request.method == 'POST':
        ingredients_str = request.form.get('ingredients', '').strip()
    else:
        # GET 也支援 URL 查詢參數
        ingredients_str = request.args.get('ingredients', '').strip()

    if ingredients_str:
        # 解析食材字串（支援逗號、頓號分隔）
        ingredient_names = []
        for name in ingredients_str.replace('、', ',').split(','):
            name = name.strip()
            if name:
                ingredient_names.append(name)

        if ingredient_names:
            recipes = recipe_model.search_by_ingredients(ingredient_names)
            if not recipes:
                flash('找不到包含這些食材的食譜，請嘗試其他食材組合。', 'info')

    return render_template('search_ingredients.html',
                           recipes=recipes,
                           ingredients_str=ingredients_str,
                           all_ingredients=all_ingredients)
