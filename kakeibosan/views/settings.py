from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from kakeibosan import db
from kakeibosan.models import User, FixedCost, Category, CategoryPaths


bp = Blueprint('settings', __name__)


@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        flash_category = 'warning'
        flash_message = f'このページでは【{request.method}】は受け付けられません'
        flash(flash_message, flash_category)
        return redirect(url_for('settings.settings'))
    else:
        category_ancestor = db.orm.aliased(Category)
        category_descendant = db.orm.aliased(Category)
        try:
            # ユーザーアカウント用
            users = db.session.query(User).order_by(User.id).all()

            # カテゴリー用
            category = db.session.query(
                Category.id,
                category_ancestor.name.label('category'),
                category_descendant.name.label('subcategory'),
                Category.in_english,
                Category.chart_color,
            ).join(category_descendant, Category.id == category_descendant.id)\
             .join(CategoryPaths, Category.id == CategoryPaths.descendant)\
             .join(category_ancestor, CategoryPaths.ancestor == category_ancestor.id)\
             .all()

            # 固定費用
            fixed_costs = db.session.query(
                FixedCost.id,
                category_ancestor.name.label('category'),
                category_descendant.name.label('subcategory'),
                FixedCost.paid_to,
                FixedCost.amount,
                FixedCost.user_id,
            ).join(category_descendant, FixedCost.category_id == category_descendant.id)\
             .join(CategoryPaths, FixedCost.category_id == CategoryPaths.descendant)\
             .join(category_ancestor, CategoryPaths.ancestor == category_ancestor.id)\
             .all()
        except db.exc.SQLAlchemyError as e:
            print(e)
            users = []
            category = []
            fixed_costs = []
        finally:
            db.session.close()

        return render_template(
            'settings.html',
            active_page='設定',
            users=users,
            category=category,
            fixed_costs=fixed_costs,
        )
