"""
recipe.py — 食譜 CRUD 路由 (Controller)

處理食譜的新增、檢視、編輯、刪除，以及「我的收藏」頁面。
使用 Flask Blueprint 組織路由，url_prefix 為空（路徑以 /recipes 開頭）。

路由清單：
    GET/POST /recipes/add          — 新增食譜
    GET      /recipes/<int:id>     — 檢視食譜詳情
    GET/POST /recipes/<int:id>/edit — 編輯食譜
    POST     /recipes/<int:id>/delete — 刪除食譜
    GET      /my-collection        — 我的收藏列表
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import recipe as recipe_model
from app.models import ingredient as ingredient_model

bp = Blueprint('recipe', __name__)


@bp.route('/recipes/add', methods=('GET', 'POST'))
def add():
    """新增食譜（含食材的多對多關聯）。

    GET  — 顯示空白的新增食譜表單。
    POST — 驗證表單資料後，建立食譜與食材關聯，成功則導向食譜詳情頁。
    """
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        portions = request.form.get('portions', '').strip()
        steps = request.form.get('steps', '').strip()
        ingredients_str = request.form.get('ingredients', '').strip()

        # 基本輸入驗證
        if not title:
            flash('食譜名稱為必填項目！', 'error')
            return render_template('recipes/form.html',
                                   title=title, portions=portions,
                                   steps=steps, ingredients_str=ingredients_str)
        if not steps:
            flash('料理步驟為必填項目！', 'error')
            return render_template('recipes/form.html',
                                   title=title, portions=portions,
                                   steps=steps, ingredients_str=ingredients_str)

        # 解析食材字串（以逗號、頓號分隔）
        ingredient_list = []
        if ingredients_str:
            for name in ingredients_str.replace('、', ',').split(','):
                name = name.strip()
                if name:
                    ingredient_list.append(name)

        # 暫時無會員系統前，將 user_id 預設為 1
        user_id = session.get('user_id', 1)

        # 轉換 portions 為整數（選填）
        portions_int = None
        if portions:
            try:
                portions_int = int(portions)
            except ValueError:
                flash('份量必須為數字！', 'error')
                return render_template('recipes/form.html',
                                       title=title, portions=portions,
                                       steps=steps, ingredients_str=ingredients_str)

        new_id = recipe_model.create({
            'user_id': user_id,
            'title': title,
            'portions': portions_int,
            'steps': steps,
            'ingredients': ingredient_list
        })

        if new_id:
            flash('食譜新增成功！', 'success')
            return redirect(url_for('recipe.detail', id=new_id))
        else:
            flash('新增食譜時發生錯誤，請稍後再試。', 'error')

    return render_template('recipes/form.html')


@bp.route('/recipes/<int:id>')
def detail(id):
    """檢視食譜詳情（含食材列表）。

    顯示食譜的標題、份量、步驟，以及關聯的所有食材。
    若食譜不存在，閃現錯誤訊息並導回收藏列表。
    """
    recipe = recipe_model.get_by_id(id)
    if not recipe:
        flash('找不到該食譜！', 'error')
        return redirect(url_for('recipe.my_collection'))
    return render_template('recipes/detail.html', recipe=recipe)


@bp.route('/recipes/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    """編輯食譜（含食材更新）。

    GET  — 顯示預填資料的編輯表單。
    POST — 驗證後更新食譜資料與食材關聯，成功則導向食譜詳情頁。
    """
    recipe = recipe_model.get_by_id(id)
    if not recipe:
        flash('找不到該食譜！', 'error')
        return redirect(url_for('recipe.my_collection'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        portions = request.form.get('portions', '').strip()
        steps = request.form.get('steps', '').strip()
        ingredients_str = request.form.get('ingredients', '').strip()

        # 基本輸入驗證
        if not title:
            flash('食譜名稱為必填項目！', 'error')
            return render_template('recipes/form.html', recipe=recipe,
                                   ingredients_str=ingredients_str)
        if not steps:
            flash('料理步驟為必填項目！', 'error')
            return render_template('recipes/form.html', recipe=recipe,
                                   ingredients_str=ingredients_str)

        # 解析食材字串
        ingredient_list = []
        if ingredients_str:
            for name in ingredients_str.replace('、', ',').split(','):
                name = name.strip()
                if name:
                    ingredient_list.append(name)

        # 轉換 portions
        portions_int = None
        if portions:
            try:
                portions_int = int(portions)
            except ValueError:
                flash('份量必須為數字！', 'error')
                return render_template('recipes/form.html', recipe=recipe,
                                       ingredients_str=ingredients_str)

        success = recipe_model.update(id, {
            'title': title,
            'portions': portions_int,
            'steps': steps,
            'ingredients': ingredient_list
        })

        if success:
            flash('食譜更新成功！', 'success')
            return redirect(url_for('recipe.detail', id=id))
        else:
            flash('更新食譜發生錯誤，請稍後再試。', 'error')

    # GET 請求：將現有食材組成逗號分隔字串，方便在表單中編輯
    ingredients_str = ', '.join(
        [ing['name'] for ing in recipe.get('ingredients', [])]
    )
    return render_template('recipes/form.html', recipe=recipe,
                           ingredients_str=ingredients_str)


@bp.route('/recipes/<int:id>/delete', methods=('POST',))
def delete(id):
    """刪除食譜（僅接受 POST 方法）。

    刪除成功或失敗都會導回「我的收藏」頁面，並閃現對應訊息。
    """
    success = recipe_model.delete(id)
    if success:
        flash('食譜已成功刪除！', 'success')
    else:
        flash('刪除食譜時發生錯誤。', 'error')
    return redirect(url_for('recipe.my_collection'))


@bp.route('/my-collection')
def my_collection():
    """我的收藏——顯示使用者建立的所有食譜。

    若使用者已登入（session 中有 user_id），只顯示該使用者的食譜；
    否則顯示所有食譜。
    """
    if 'user_id' in session:
        recipes = recipe_model.get_by_user_id(session['user_id'])
    else:
        recipes = recipe_model.get_all()

    return render_template('recipes/list.html', recipes=recipes)
