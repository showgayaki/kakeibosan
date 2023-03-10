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

    category = ('固定費', '光熱費', '食費', '日用品', '交通費')
    sub_categories = ('電気代', 'ガス代', '水道代')

    total_costs_last_12_months = _total_costs_last_12_months(this_month)
    costs_this_month_by_category = _costs_this_month_by_category(this_month, category)
    utility_costs = _utility_costs_last_12_months(sub_categories, total_costs_last_12_months['months'])

    # 「○月」の形にする
    total_costs_last_12_months['months'] = [month.strftime('%-m月') for month in total_costs_last_12_months['months']]

    return render_template(
        'dashboard.html',
        active_page='ダッシュボード',
        this_month=this_month,
        total_costs_last_12_months=total_costs_last_12_months,
        costs_this_month_by_category=costs_this_month_by_category,
        utility_costs=utility_costs
    )


def _total_costs_last_12_months(this_month):
    # 直近12ヶ月の支出合計（ページ上部の折れ線グラフ用）
    MONTH_COUNT = 12
    last_12_months = []
    total_costs_per_month = []
    # 今月分からひと月ごとに遡って、直近12ヶ月分を合計していく
    for i in range(MONTH_COUNT):
        month = (this_month + relativedelta(months=-i))
        last_12_months.append(month)
        try:
            costs = Cost.query.filter_by(month_to_add=month).all()
        except exc.SQLAlchemyError:
            costs = {}
        finally:
            db.session.close()

        total = sum(cost.amount for cost in costs)
        total_costs_per_month.append(total)

    # 降順に並べ替えて返す
    total_dict = {'months': last_12_months[::-1], 'total': total_costs_per_month[::-1]}
    return total_dict


def _costs_this_month_by_category(this_month, category):
    # 今月のカテゴリー別支出（円グラフ用）
    costs_by_category = []
    for cat in category:
        try:
            costs = Cost.query.filter(and_(Cost.month_to_add == this_month, Cost.category == cat)).all()
            total_dict = {'category': cat, 'amount': sum(cost.amount for cost in costs)}
            costs_by_category.append(total_dict)
        except AttributeError:
            costs_by_category[cat] = 0
        finally:
            db.session.close()

    return costs_by_category


def _utility_costs_last_12_months(sub_categories, months):
    # 直近12か月分の水道光熱費（各カードの折れ線ブラフ用）
    utility_costs = {}
    for month in months:
        utility_costs_per_month = {}
        for sc in sub_categories:
            try:
                cost = Cost.query.filter(
                    and_(Cost.sub_category == sc, Cost.month_to_add == month)).order_by(Cost.id).first()
                utility_costs_per_month[sc] = cost.amount
            except AttributeError:
                utility_costs_per_month[sc] = 0
            finally:
                db.session.close()
        utility_costs['{0:%Y-%m}'.format(month)] = utility_costs_per_month

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
