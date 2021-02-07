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
        costs = Cost.query.filter_by(month_to_add=month_to_add).order_by(Cost.id).all()
        users = User.query.order_by(User.id).all()
    except exc.SQLAlchemyError:
        costs = {}
        users = {}
    finally:
        db.session.close()
    total_costs = {}
    total = 0

    for user in users:
        user_total = 0
        for cost in costs:
            if user.id == cost.user_id:
                user_total += cost.amount
                total += cost.amount
        total_costs[user.view_name] = user_total

    pay_by = min(total_costs, key=total_costs.get)
    amount = (max(total_costs.values()) - min(total_costs.values())) / len(total_costs)

    total_costs['合計'] = total
    total_costs['折半額'] = Decimal(str(total / len(users))).quantize(Decimal('0'), rounding=ROUND_HALF_UP)
    total_costs['{}支払額'.format(pay_by)] = Decimal(str(amount)).quantize(Decimal('0'), rounding=ROUND_HALF_UP)

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
            if val is not None and key == 'bought_in':
                cost_dict[key] = '{0:%Y-%-m-%-d}'.format(val)
            elif val is not None and key == 'month_to_add':
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
