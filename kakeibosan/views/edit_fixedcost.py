from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_required
from kakeibosan import db
from kakeibosan.views.forms import EditFixedCost
from kakeibosan.models import FixedCost, Category, CategoryPaths


bp = Blueprint('edit_fixedcost', __name__)


@bp.route('/settings/fixed_cost', methods=['GET', 'POST'])
@login_required
def edit_fixedcost():
    form = EditFixedCost()
    record_id = request.args.get('record_id')

    if request.method == 'POST':
        flash_category = 'info'
        # サブカテゴリー名からcategory_idを取得
        category_id = (db.session.query(Category).filter(Category.name == form.subcategory.data).first()).id
        if record_id:
            # record_idがあるときは既存レコードの更新
            fixed_cost = db.session.query(FixedCost).filter(FixedCost.id == record_id).first()
            flash_message = '{}:{}を更新しました'.format(form.category.data, form.subcategory.data)
        else:
            fixed_cost = FixedCost()
            flash_message = '{}:{}を追加しました'.format(form.category.data, form.subcategory.data)

        fixed_cost.category_id = category_id
        fixed_cost.paid_to = form.paid_to.data
        fixed_cost.amount = form.amount.data
        fixed_cost.user_id = form.username.data

        try:
            db.session.add(fixed_cost)
            db.session.commit()
        except db.exc.SQLAlchemyError:
            flash_category = 'warning'
            flash_message = 'Insert Error'
        finally:
            db.session.close()

        flash(flash_message, flash_category)
        return redirect(url_for('settings.settings'))
    else:
        if record_id:
            # カテゴリー・サブカテゴリーの結合用に、Categoryテーブルをそれぞれ別名で定義しておく
            category_ancestor = db.orm.aliased(Category)
            category_descendant = db.orm.aliased(Category)

            # テーブルを結合して固定費を取得
            fixed_cost = db.session.query(
                FixedCost.id,
                category_ancestor.name.label('category'),
                category_descendant.name.label('subcategory'),
                FixedCost.paid_to,
                FixedCost.amount,
                FixedCost.user_id,
            ).filter(FixedCost.id == record_id)\
             .join(category_descendant, FixedCost.category_id == category_descendant.id)\
             .join(CategoryPaths, FixedCost.category_id == CategoryPaths.descendant)\
             .join(category_ancestor, CategoryPaths.ancestor == category_ancestor.id)\
             .first()

            active_page = '固定費更新'
            form.username.default = fixed_cost.user_id
            form.process()
            form.category.data = fixed_cost.category
            form.subcategory.data = fixed_cost.subcategory
            form.paid_to.data = fixed_cost.paid_to
            form.amount.data = fixed_cost.amount
        else:
            active_page = '固定費追加'
        return render_template('edit_fixedcost.html', form=form, active_page=active_page,
                               record_id=record_id)
