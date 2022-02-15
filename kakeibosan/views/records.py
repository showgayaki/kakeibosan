from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import render_template, request, abort, jsonify, flash
from flask_login import login_required
from sqlalchemy import exc
from kakeibosan import app, db
from kakeibosan.models import User, FixedCost, Cost


@app.route('/kakeibosan/records', methods=['GET', 'POST'])
@login_required
def records():
    if request.method == 'POST':
        records_json = request.json
        flash_list = []
        for record in records_json:
            if record['id'] is None:
                cost = Cost()
                created_at = datetime.now()
            else:
                try:
                    cost = Cost.query.filter_by(id=record['id']).first()
                except exc.SQLAlchemyError:
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
            try:
                users = User.query.order_by(User.id).all()
            except exc.SQLAlchemyError:
                users = {}
            finally:
                db.session.close()

            costs = _fetch_view_costs(view_month)
            users_list = []
            for user in users:
                user_dict = user.to_dict()
                user_dict['password'] = ''
                users_list.append(user_dict)

            total_cost = _cost_per_month(view_month.date())
            month = _month_pager(view_month, oldest_month)

            cost_records = _cost_records(costs)
            view_month = view_month.date()
            return render_template('records.html', active_page='データ一覧・登録', users=users_list,
                                   costs=cost_records, month=month, view_month=view_month, total_cost=total_cost)
        else:
            abort(404)


def _insert_costs(record, cost, created_at):
    try:
        if not record['del']:
            cost.id = record['id']
            cost.is_paid_in_advance = record['is_paid_in_advance']
            cost.category = record['category']
            cost.sub_category = record['sub_category']
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
    except exc.SQLAlchemyError:
        if record['user_id'] > 0:
            flash_message = 'add_error' if record['id'] is None else 'update_error'
        else:
            flash_message = 'delete_error'
    finally:
        db.session.close()

    return flash_message


def _fetch_view_costs(view_month):
    try:
        # 計上月で検索
        costs = Cost.query.filter_by(month_to_add=view_month.date()).all()
    except exc.SQLAlchemyError:
        costs = {}
    finally:
        db.session.close()
    return costs


def _cost_per_month(month_to_add):
    try:
        # 折半するレコード取得
        costs_split = Cost.query.filter_by(month_to_add=month_to_add).filter(
            (Cost.is_paid_in_advance == False) | (Cost.is_paid_in_advance == None)).order_by(Cost.id).all()

        # 立替したレコード取得
        costs_paid_in_advance = Cost.query.filter_by(
            month_to_add=month_to_add, is_paid_in_advance=True).order_by(Cost.id).all()

        users = User.query.order_by(User.id).all()
    except exc.SQLAlchemyError:
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

    print(advance_subtraction)
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


def _cost_records(costs):
    cost_records = []
    for cost in costs:
        cost_dict = cost.to_dict().copy()
        for key, val in cost_dict.items():
            if key == 'bought_in' and val is not None:
                cost_dict[key] = '{0:%Y-%-m-%-d}'.format(val)
            elif key == 'month_to_add' and val is not None:
                cost_dict[key] = '{0:%Y-%-m}'.format(val)
            elif key == 'created_at':
                cost_dict[key] = '{0:%Y-%m-%d %H:%M:%S}'.format(val)
            elif key == 'updated_at':
                cost_dict[key] = '{0:%Y-%m-%d %H:%M:%S}'.format(val)
        cost_records.append(cost_dict)

    return cost_records


def _flash_message(flash_list):
    flash_dict = {
        'add': 'を追加しました。'
        , 'update': 'を更新しました。'
        , 'delete': 'を削除しました。'
        , 'add_error': 'の追加に失敗しました。'
        , 'update_error': 'の更新に失敗しました。'
        , 'delete_error': 'の削除に失敗しました。'
    }
    for key, val in flash_dict.items():
        category = 'warning' if 'error' in key else 'info'
        if flash_list.count(key) > 0:
            flash('{}件のレコード{}'.format(flash_list.count(key), val), category)
