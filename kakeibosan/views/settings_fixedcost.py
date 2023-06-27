from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_required
from kakeibosan import db
from kakeibosan.views.forms import SettingsFixedCost
from kakeibosan.models import FixedCost, Category, CategoryPaths


bp = Blueprint('settings_fixedcost', __name__)


@bp.route('/settings/fixed-cost', methods=['GET', 'POST'])
@login_required
def settings_fixedcost():
    form = SettingsFixedCost()
    record_id = request.args.get('record_id')

    if request.method == 'POST':
        flash_category = 'info'
        # 選択したサブカテゴリーからcategory_idを取得
        subcategory_id = form.subcategory_select.data.split('-')[1]
        update_target_category = db.session.query(Category).filter(Category.id == subcategory_id).first()

        if record_id:
            # record_idがあるときは既存レコードの更新
            fixed_cost = db.session.query(FixedCost).filter(FixedCost.id == record_id).first()
        else:
            fixed_cost = FixedCost()

        fixed_cost.category_id = update_target_category.id
        fixed_cost.paid_to = form.paid_to.data
        fixed_cost.amount = form.amount.data
        fixed_cost.user_id = form.username.data

        try:
            db.session.add(fixed_cost)
            db.session.flush()
            db.session.commit()

            flash_message = 'ID:{} ({})を'.format(fixed_cost.id, update_target_category.name)
            flash_message += '更新しました' if record_id else '追加しました'
        except db.exc.SQLAlchemyError as e:
            flash_category = 'warning'
            flash_message = str(e)
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
                category_ancestor.id.label('category'),
                category_descendant.id.label('subcategory'),
                FixedCost.paid_to,
                FixedCost.amount,
                FixedCost.user_id,
            ).filter(FixedCost.id == record_id)\
             .join(category_descendant, FixedCost.category_id == category_descendant.id)\
             .join(CategoryPaths, FixedCost.category_id == CategoryPaths.descendant)\
             .join(category_ancestor, CategoryPaths.ancestor == category_ancestor.id)\
             .first()

            active_page = '固定費更新'
            form.category_select.default = fixed_cost.category
            form.subcategory_select.default = '{}-{}'.format(fixed_cost.category, fixed_cost.subcategory)
            form.username.default = fixed_cost.user_id
            form.process()
            form.paid_to.data = fixed_cost.paid_to
            form.amount.data = fixed_cost.amount
        else:
            active_page = '固定費追加'
        return render_template(
            'settings_fixedcost.html',
            form=form,
            active_page=active_page,
            record_id=record_id
        )
