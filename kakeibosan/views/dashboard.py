from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import Blueprint, render_template
from sqlalchemy import exc, and_
from flask_login import login_required
from kakeibosan import db
from kakeibosan.models import Cost, FixedCost


bp = Blueprint('dashboard', __name__)


@bp.route('/')
@login_required
def dashboard():
    this_month = datetime.today().date().replace(day=1)
    _insert_fixed_costs(this_month)

    sub_categories = ('電気代', 'ガス代', '水道代')
    total_per_months = _total_per_months(this_month)

    category = ('固定費', '光熱費', '食費', '日用品', '交通費')
    costs_per_month = _costs_per_month(this_month, category)

    utility_costs = _utility_per_month(sub_categories, total_per_months['months'])

    # グラフ用に配列を逆順にする->[::-1]
    total_per_months['total'] = total_per_months['total'][::-1]
    total_per_months['months'] = [month.strftime('%-m月') for month in total_per_months['months']][::-1]

    return render_template('dashboard.html', active_page='ダッシュボード', this_month=this_month,
                           total_per_months=total_per_months, costs_per_month=costs_per_month,
                           utility_costs=utility_costs)


def _total_per_months(this_month):
    month_count = 12
    last_12_months = []
    total_costs = []
    for i in range(month_count):
        month = (this_month + relativedelta(months=-i))
        last_12_months.append(month)
        try:
            costs = Cost.query.filter_by(month_to_add=month).all()
        except exc.SQLAlchemyError:
            costs = {}
        finally:
            db.session.close()
        total = 0
        total += sum(cost.amount for cost in costs)
        total_costs.append(total)

    total_dict = {'months': last_12_months, 'total': total_costs}
    return total_dict


def _costs_per_month(this_month, category):
    cost_per_month = []
    for cat in category:
        try:
            costs = Cost.query.filter(and_(Cost.month_to_add == this_month, Cost.category == cat)).all()
            total_dict = {'category': cat, 'amount': sum(cost.amount for cost in costs)}
            cost_per_month.append(total_dict)
        except AttributeError:
            cost_per_month[cat] = 0
        finally:
            db.session.close()
    return cost_per_month


def _utility_per_month(sub_categories, months):
    utility_costs = {}
    for month in months:
        utility_charnge = {}
        for sc in sub_categories:
            try:
                cost = Cost.query.filter(
                    and_(Cost.sub_category == sc, Cost.month_to_add == month)).order_by(Cost.id).first()
                utility_charnge[sc] = cost.amount
            except AttributeError:
                utility_charnge[sc] = 0
            finally:
                db.session.close()
        utility_costs['{0:%Y-%m}'.format(month)] = utility_charnge

    return utility_costs


def _insert_fixed_costs(month_to_add):
    # 固定費を取得
    try:
        fixed_costs = FixedCost.query.order_by(FixedCost.id).all()
    except exc.SQLAlchemyError:
        fixed_costs = {}
    finally:
        db.session.close()

    # 今月のコストを取得
    try:
        costs = Cost.query.filter_by(month_to_add=month_to_add).all()
    except exc.SQLAlchemyError:
        costs = {}
    finally:
        db.session.close()

    # 今月のコストにまだ固定費が入ってなければインサート
    for fc in fixed_costs:
        found = False
        for cost in costs:
            if fc.sub_category == cost.sub_category:
                found = True
                break

        if not found:
            now = datetime.now()

            cost = Cost()
            cost.category = fc.category
            cost.sub_category = fc.sub_category
            cost.paid_to = fc.paid_to
            cost.amount = fc.amount
            cost.month_to_add = month_to_add
            cost.bought_in = month_to_add
            cost.created_at = now
            cost.updated_at = now
            cost.user_id = fc.user_id
            try:
                db.session.add(cost)
                db.session.commit()
            except exc.SQLAlchemyError:
                pass
            finally:
                db.session.close()
