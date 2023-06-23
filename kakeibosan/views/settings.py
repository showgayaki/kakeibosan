from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from kakeibosan import db
from kakeibosan.models import User, FixedCost, Category, CategoryPaths


bp = Blueprint('settings', __name__)


@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        parameter = request.args.get('card')
        if parameter == 'add_account':
            return redirect(url_for('edit_account.edit_account', edit='add'))
        elif parameter == 'fixedcost':
            return redirect(url_for('edit_fixedcost.edit_fixedcost', edit='add'))
    else:
        category_ancestor = db.orm.aliased(Category)
        category_descendant = db.orm.aliased(Category)
        try:
            users = db.session.query(User).order_by(User.id).all()
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
        except db.exc.SQLAlchemyError:
            users = []
            fixed_costs = []
        finally:
            db.session.close()

        return render_template(
            'settings.html',
            active_page='設定',
            fixed_costs=fixed_costs,
            users=users,
        )
