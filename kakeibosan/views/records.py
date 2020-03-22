from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import render_template, request, abort, jsonify, flash
from flask_login import login_required
from sqlalchemy import and_, exc
from kakeibosan import app, db
from kakeibosan.models import User, FixedCost, Cost


@app.route('/kakeibosan/records', methods=['GET', 'POST'])
@login_required
def records():
    if request.method == 'POST':
        records_json = request.json
        for record in records_json:
            if record['id'] is None:
                cost = Cost()
                created_at = datetime.now()
            else:
                cost = Cost.query.filter(Cost.id == record['id']).first()
                created_at = datetime.strptime(record['created_at'], '%Y-%m-%d %H:%M:%S')

            flash_message, flash_category = _insert_costs(record, cost, created_at)
            flash(flash_message, flash_category)
        return jsonify(success=True)
    else:
        # 集計開始月を設定
        oldest_month = datetime.strptime('2019-05-01', '%Y-%m-%d')
        parameter = request.args.get('month')
        view_month = (datetime.strptime(parameter + '-01', '%Y-%m-%d') if parameter
                      else datetime.today().replace(day=1, hour=0, minute=0, second=0, microsecond=0))

        if view_month > oldest_month:
            users = User.query.order_by(User.id).all()
            users_list = [user.to_dict() for user in users]
            fixed_costs = FixedCost.query.order_by(FixedCost.id).all()

            total_cost = _cost_per_month(view_month.date())
            month = _month_pager(view_month, oldest_month)

            # 「>= *月1日00:00:00」だと1日分が表示されないので、seconds=-1している
            end_of_month = view_month + relativedelta(months=1, seconds=-1)
            costs = Cost.query.filter(and_(Cost.bought_in >= view_month + relativedelta(seconds=-1)
                                           , Cost.bought_in <= end_of_month)).order_by(Cost.id).all()
            db.session.close()

            cost_records = _cost_records(costs)
            _insert_fixed_costs(costs, fixed_costs, view_month.date())

            view_month = view_month.strftime('%Y年%-m月')

            return render_template('records.html', active_page='データ一覧・登録', users=users_list,
                                   costs=cost_records, month=month, view_month=view_month, total_cost=total_cost)
        else:
            abort(404)


def _insert_costs(record, cost, created_at):
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

    try:
        db.session.add(cost)
        db.session.commit()
        flash_message = 'レコードを更新しました'
        flash_category = 'info'
    except exc.SQLAlchemyError:
        flash_message = 'Insert Error'
        flash_category = 'warning'
    finally:
        db.session.close()

    return flash_message, flash_category


def _insert_fixed_costs(costs, fixed_costs, month_to_add):
    for fc in fixed_costs:
        found = False
        for cost in costs:
            if fc.sub_category == cost.sub_category:
                found = True
                break
        if not found:
            cost = Cost()
            cost.category = '固定費'
            cost.sub_category = fc.sub_category
            cost.paid_to = fc.paid_to
            cost.amount = fc.amount
            cost.month_to_add = month_to_add
            cost.bought_in = month_to_add
            cost.user_id = fc.user_id
            try:
                db.session.add(cost)
                db.session.commit()
            except exc.SQLAlchemyError:
                pass
            finally:
                db.session.close()


def _cost_per_month(month_to_add):
    costs = Cost.query.filter_by(month_to_add=month_to_add).order_by(Cost.id).all()
    users = User.query.order_by(User.id).all()
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
