from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_required
from kakeibosan import db
from kakeibosan.views.forms import SettingsCagegory
from kakeibosan.models import Category, CategoryPaths


bp = Blueprint('settings_category', __name__)


@bp.route('/settings/category', methods=['GET', 'POST'])
@login_required
def settings_category():
    form = SettingsCagegory()
    record_id = request.args.get('record_id')
    category_type = request.args.get('type')

    if request.method == 'POST':
        flash_message = ''
        flash_category = 'info'

        flash(flash_message, flash_category)
        return redirect(url_for('settings.settings'))
    else:
        if record_id:
            # カテゴリー・サブカテゴリーの結合用に、Categoryテーブルをそれぞれ別名で定義しておく
            category_ancestor = db.orm.aliased(Category)
            category_descendant = db.orm.aliased(Category)

            # テーブルを結合して固定費を取得
            category = db.session.query(
                Category.id,
                category_ancestor.id.label('ancestor'),
                category_ancestor.name.label('category'),
                category_descendant.id.label('descendant'),
                Category.in_english,
                Category.chart_color,
            ).filter(Category.id == record_id)\
             .join(category_descendant, Category.id == category_descendant.id)\
             .join(CategoryPaths, Category.id == CategoryPaths.descendant)\
             .join(category_ancestor, CategoryPaths.ancestor == category_ancestor.id)\
             .first()

            active_page = 'カテゴリー更新'
            if category_type is None:
                form.category.default = category.ancestor
                form.subcategory.default = '{}-{}'.format(category.ancestor, category.descendant)
                form.process()
                form.in_english.data = category.in_english
                form.chart_color.data = category.chart_color
            else:
                form.category_parent.data = category.category
        else:
            active_page = 'カテゴリー追加'
        return render_template(
            'settings_category.html',
            form=form,
            active_page=active_page,
            type=category_type,
        )
