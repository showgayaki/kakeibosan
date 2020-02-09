from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import render_template
from sqlalchemy import and_
from flask_login import login_required
from kakeibosan import app
from kakeibosan.models import Cost


@app.route('/kakeibosan/')
@login_required
def dashboard():
    this_month = datetime.today().date().replace(day=1)

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
        costs = Cost.query.filter_by(month_to_add=month).all()
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
        utility_costs['{0:%Y-%m}'.format(month)] = utility_charnge

    return utility_costs
