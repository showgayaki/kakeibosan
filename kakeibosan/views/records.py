from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import Blueprint, render_template, request, abort, jsonify, flash
from flask_login import login_required
from kakeibosan import db
from kakeibosan.models import User, Cost, Category, CategoryPaths


bp = Blueprint('records', __name__)


@bp.route('/records', methods=['GET', 'POST'])
@login_required
def records():
    if request.method == 'POST':
        records_json = request.json
        flash_list = []
        for record in records_json:
            # idがない場合は新規登録
            if record['id'] is None:
                cost = Cost()
                created_at = datetime.now()
            else:
                try:
                    cost = db.session.query(Cost).filter_by(id=record['id']).first()
                except db.exc.SQLAlchemyError:
                    cost = {}
                finally:
                    db.session.close()
                created_at = datetime.strptime(record['created_at'], '%Y-%m-%d %H:%M:%S')

            flash_list.append(_insert_costs(record, cost, created_at))

        _flash_message(flash_list)
        return jsonify(success=True)
    else:
        # 集計開始月を設定
        oldest_month = datetime.strptime('2019-05-01', '%Y-%m-%d')
        parameter = request.args.get('month')
        this_month = datetime.today().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        view_month = datetime.strptime(parameter + '-01', '%Y-%m-%d') if parameter else this_month
        next_month = (this_month + relativedelta(months=1))

        if oldest_month < view_month < next_month:
            user_list = _user_list()
            category_list = _category_list()

            costs = _fetch_view_costs(view_month)
            total_detail = _fetch_total_detail(view_month.date())
            month = _month_pager(view_month, oldest_month)

            return render_template(
                'records.html',
                active_page='データ一覧・登録',
                users=user_list,
                costs=costs,
                month=month,
                view_month=view_month.date(),
                total_detail=total_detail,
                category_dict=category_list,
            )
        else:
            abort(404)


def _user_list():
    user_list = []
    try:
        users = db.session.query(User).order_by(User.id).all()
        for user in users:
            user_dict = user.to_dict()
            user_dict['password'] = ''
            user_list.append(user_dict)
    except db.exc.SQLAlchemyError:
        users = {}
    finally:
        db.session.close()

    return user_list


def _category_list():
    category_list = []
    try:
        category = db.session.query(
            CategoryPaths.ancestor,
            CategoryPaths.descendant,
            Category.name
        ).join(Category, CategoryPaths.descendant == Category.id).all()

        # [{'固定費': ['家賃', '管理費', '手数料', '更新料', '駐輪場']},...]の形にする
        subcategory_list = []
        category_name = ''
        for cat in category:
            if cat.ancestor == cat.descendant:
                if len(subcategory_list) > 0:
                    category_list.append({category_name: subcategory_list})
                subcategory_list = []
                category_name = cat.name
            else:
                subcategory_list.append(cat.name)
        category_list.append({category_name: subcategory_list})
    except db.exc.SQLAlchemyError:
        category = []
    finally:
        db.session.close()

    return category_list


def _insert_costs(record, cost, created_at):
    try:
        if not record['del']:
            category = db.session.query(Category).filter(Category.name == record['subcategory']).first()
            category_id = category.id

            cost.id = record['id']
            cost.is_paid_in_advance = record['is_paid_in_advance']
            cost.category_id = category_id
            cost.paid_to = record['paid_to']
            cost.amount = record['amount']
            cost.month_to_add = datetime.strptime(record['month_to_add'] + '-01', '%Y-%m-%d')
            cost.bought_in = datetime.strptime(record['bought_in'], '%Y-%m-%d')
            cost.created_at = created_at
            cost.updated_at = datetime.now()
            cost.user_id = record['user_id']
            db.session.add(cost)
            flash_message = 'add' if record['id'] is None else 'update'
        else:
            db.session.delete(cost)
            flash_message = 'delete'

        db.session.commit()
    except db.exc.SQLAlchemyError:
        if record['user_id'] > 0:
            flash_message = 'add_error' if record['id'] is None else 'update_error'
        else:
            flash_message = 'delete_error'
    finally:
        db.session.close()

    return flash_message


def _fetch_view_costs(view_month):
    # カテゴリー・サブカテゴリーの結合用に、Categoryテーブルをそれぞれ別名で定義しておく
    category_ancestor = db.orm.aliased(Category)
    category_descendant = db.orm.aliased(Category)
    try:
        # 計上月で検索
        # category_idでCategoryを結合してサブカテゴリー名を取得
        # category_idでCategoryPathsを結合
        # 結合したCategoryPathsのancestorとCategory.idで結合
        # Category.id(ancestor)の名前(カテゴリー名)を取得
        costs = db.session.query(
            Cost.id,
            category_ancestor.name.label('category'),
            category_descendant.name.label('subcategory'),
            Cost.paid_to,
            Cost.amount,
            Cost.month_to_add,
            Cost.bought_in,
            Cost.user_id,
        ).filter_by(month_to_add=view_month.date())\
         .join(category_descendant, Cost.category_id == category_descendant.id)\
         .join(CategoryPaths, Cost.category_id == CategoryPaths.descendant)\
         .join(category_ancestor, CategoryPaths.ancestor == category_ancestor.id)\
         .all()

        # dictionaryに変換
        costs = [
            {
                'id': row.id,
                'category': row.category,
                'subcategory': row.subcategory,
                'paid_to': row.paid_to,
                'amount': row.amount,
                'month_to_add': '{0:%Y-%-m}'.format(row.month_to_add),
                'bought_in': '{0:%Y-%-m-%-d}'.format(row.bought_in),
                'user_id': row.user_id,
            } for row in costs
        ]
    except db.exc.SQLAlchemyError:
        costs = {}
    finally:
        db.session.close()

    return costs


def _fetch_total_detail(month_to_add):
    try:
        # 折半するレコード取得
        costs_split = db.session.query(Cost).filter_by(month_to_add=month_to_add).filter(
            (Cost.is_paid_in_advance == False) | (Cost.is_paid_in_advance == None)).order_by(Cost.id).all()

        # 立替したレコード取得
        costs_paid_in_advance = db.session.query(Cost).filter_by(
            month_to_add=month_to_add, is_paid_in_advance=True).order_by(Cost.id).all()

        users = db.session.query(User).order_by(User.id).all()
    except db.exc.SQLAlchemyError:
        costs_split = {}
        costs_paid_in_advance = {}
        users = {}
    finally:
        db.session.close()

    total_costs = {}
    total_paid_in_advance = {}
    total_amount = 0

    for user in users:
        user_total_split = 0
        # 折半金額と合計の計算
        for cs in costs_split:
            if user.id == cs.user_id:
                user_total_split += cs.amount
                total_amount += cs.amount
        total_costs[user.view_name] = user_total_split

        # 立替金額集計
        user_total_paid_in_advance = 0
        for cp in costs_paid_in_advance:
            if user.id == cp.user_id:
                user_total_paid_in_advance += cp.amount
        # keyに金額、valに名前を入れておく
        total_paid_in_advance[user_total_paid_in_advance] = user.view_name
        total_costs[user.view_name + '立替額'] = user_total_paid_in_advance

    split_total = Decimal(str(total_amount / len(users))).quantize(Decimal('0'), rounding=ROUND_HALF_UP)

    # 立替金額の多い方はどっち
    subtraction_name = (
        total_paid_in_advance[max(total_paid_in_advance.keys())]
        if max(total_paid_in_advance.keys()) != min(total_paid_in_advance.keys()) else ''
    )
    # 立替金額の多い方dictionary
    advance_subtraction = {
        'name': subtraction_name,
        'amount': max(total_paid_in_advance.keys()) - min(total_paid_in_advance.keys())
    }
    # すべての差引
    subtraction = {}
    for user in users:
        advance_amount = (
            advance_subtraction['amount']
            if user.view_name == advance_subtraction['name']
            else -advance_subtraction['amount']
        )
        subtraction[user.view_name] = total_costs[user.view_name] - split_total + advance_amount

    for key, val in subtraction.items():
        if val < 0:
            pay_by = key
            to_pay = abs(val)

    total_costs['折半合計'] = total_amount
    total_costs['折半額'] = split_total
    # 改行したいところに半角スペースを入れておく、テンプレート側で処理
    advance_key = '立替差引' + (' ({})'.format(advance_subtraction['name']) if advance_subtraction['name'] != '' else '')
    total_costs[advance_key] = advance_subtraction['amount']
    total_costs['{} 支払額'.format(pay_by)] = to_pay

    return total_costs


def _month_pager(view_month, oldest_month):
    is_oldest = (view_month + relativedelta(months=-1)).replace(day=1) == oldest_month

    prev_month = ('' if is_oldest
                  else (view_month + relativedelta(months=-1)).replace(day=1).strftime('%Y-%m'))

    is_next_month_future = (view_month + relativedelta(months=1)).replace(day=1) > datetime.today()
    next_month = ('' if is_next_month_future
                  else (view_month + relativedelta(months=1)).replace(day=1).strftime('%Y-%m'))

    month = {'prev': prev_month, 'next': next_month}
    return month


def _flash_message(flash_list):
    flash_dict = {
        'add': 'を追加しました。',
        'update': 'を更新しました。',
        'delete': 'を削除しました。',
        'add_error': 'の追加に失敗しました。',
        'update_error': 'の更新に失敗しました。',
        'delete_error': 'の削除に失敗しました。',
    }
    for key, val in flash_dict.items():
        category = 'warning' if 'error' in key else 'info'
        if flash_list.count(key) > 0:
            flash('{}件のレコード{}'.format(flash_list.count(key), val), category)
