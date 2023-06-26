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
        if record_id:
            update_target_record = _fetch_category_record(record_id)
        else:
            update_target_record = Category()

        flash_category, flash_message = _update_category_record(category_type, form, update_target_record)

        flash(flash_message, flash_category)
        return redirect(url_for('settings.settings'))
    else:
        if record_id:
            # カテゴリー・サブカテゴリーの結合用に、Categoryテーブルをそれぞれ別名で定義しておく
            category_ancestor = db.orm.aliased(Category)
            category_descendant = db.orm.aliased(Category)

            # テーブルを結合して固定費を取得
            update_target_record = db.session.query(
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
            if category_type == 'parent':
                form.category.data = update_target_record.category
            else:
                form.category_select.default = update_target_record.ancestor
                form.subcategory_select.default = '{}-{}'.format(update_target_record.ancestor, update_target_record.descendant)
                form.process()
                form.in_english.data = update_target_record.in_english
                form.chart_color.data = update_target_record.chart_color
        else:
            active_page = 'カテゴリー追加'
        return render_template(
            'settings_category.html',
            form=form,
            active_page=active_page,
            type=category_type,
            record_id=record_id,
        )


def _fetch_category_record(record_id):
    try:
        update_target_record = db.session.query(Category).filter(Category.id == record_id).first()
    except db.exc.SQLAlchemyError as e:
        print(e)
        update_target_record = None
    finally:
        db.session.close()

    return update_target_record


def _update_category_record(category_type, form, update_target_record):
    PARENT_CATEGORY_INTERVAL = 100
    flash_message = ''
    flash_category = 'info'
    category_paths = None

    if category_type == 'parent':
        if update_target_record.id is None:
            # 親カテゴリーの新規追加
            # 親カテゴリーのidは100で割り切れる数
            last_parent_category = db.session.query(Category)\
                .filter((Category.id % PARENT_CATEGORY_INTERVAL) == 0)\
                .order_by(Category.id.desc())\
                .first()

            # 新規追加されるidは、最大値＋100
            update_target_record.id = last_parent_category.id + PARENT_CATEGORY_INTERVAL
            update_target_record.name = form.category_parent.data

            # 新規追加なのでCategoryPathsにも追加する（親カテゴリーなのでancestorとdescendantは同じ値）
            category_paths = CategoryPaths()
            category_paths.ancestor = update_target_record.id
            category_paths.descendant = update_target_record.id
            flash_message = f'カテゴリーID: {update_target_record.id} （{update_target_record.name}）を追加しました'
        else:
            # 親カテゴリーの既存レコード更新
            update_target_record.name = form.category_parent.data
            flash_message = f'カテゴリーID: {update_target_record.id} （{update_target_record.name}）を更新しました'
    else:
        if update_target_record.id is None:
            # サブカテゴリーの新規追加
            # 選択した親カテゴリーと同じ百番代の最大idを取得
            last_subcategory = db.session.query(Category)\
                .filter((Category.id - form.category_select.data) < PARENT_CATEGORY_INTERVAL)\
                .order_by(Category.id.desc())\
                .first()

            update_target_record.id = last_subcategory.id + 1
            update_target_record.name = form.subcategory.data
            update_target_record.in_english = None if form.in_english.data == '' else form.in_english.data
            update_target_record.chart_color = None if form.chart_color.data == '' else form.chart_color.data

            # CategoryPathsにも追加
            category_paths = CategoryPaths()
            category_paths.ancestor = form.category_select.data
            category_paths.descendant = update_target_record.id
            flash_message = f'カテゴリーID: {update_target_record.id} （{update_target_record.name}）を追加しました'
        else:
            # サブカテゴリーの既存レコード更新
            update_target_record.in_english = None if form.in_english.data == '' else form.in_english.data
            update_target_record.chart_color = None if form.chart_color.data == '' else form.chart_color.data
            flash_message = f'カテゴリーID: {update_target_record.id} （{update_target_record.name}）を更新しました'

    try:
        if category_paths:
            db.session.add(category_paths)

        db.session.add(update_target_record)
        db.session.commit()
    except db.exc.SQLAlchemyError as e:
        flash_category = 'warning'
        flash_message = f'{e}'
    finally:
        db.session.close()

    return flash_category, flash_message
