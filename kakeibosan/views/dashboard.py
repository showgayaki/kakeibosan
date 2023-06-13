from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import Blueprint, render_template
from flask_login import login_required
from kakeibosan import db
from kakeibosan.models import Cost, FixedCost, Category, CategoryPaths


bp = Blueprint('dashboard', __name__)


@bp.route('/')
@login_required
def dashboard():
    this_month = datetime.today().date().replace(day=1)
    _insert_fixed_costs(this_month)

    try:
        # 親カテゴリを取得（出費割合グラフ用）
        category_parent = db.session.query(Category).filter(Category.id == CategoryPaths.ancestor).all()
        # 折れ線グラフを表示させるカテゴリを取得（表示させる場合は、chart_colorが設定されている）
        view_category = db.session.query(Category).filter(Category.chart_color != None).all()

        view_category_ids = []
        view_category_list = []
        for vc in view_category:
            view_category_ids.append(vc.id)
            view_category_list.append(vc.to_dict())
    except db.exc.SQLAlchemyError:
        category_parent = None
    finally:
        db.session.close()

    # ダッシュボード一番上の大きい折れ線グラフ用
    total_costs_last_12_months = _total_costs_last_12_months(this_month)
    # 当月の出費割合円グラフ用
    costs_this_month_by_category = _costs_this_month_by_category(this_month, category_parent)
    # 光熱費折れ線グラフ用
    utility_costs = _utility_costs_last_12_months(view_category_ids, total_costs_last_12_months['months'])

    # 「○月」の形にする
    total_costs_last_12_months['months'] = [month.strftime('%-m月') for month in total_costs_last_12_months['months']]

    return render_template(
        'dashboard.html',
        active_page='ダッシュボード',
        this_month=this_month,
        total_costs_last_12_months=total_costs_last_12_months,
        costs_this_month_by_category=costs_this_month_by_category,
        utility_costs=utility_costs,
        view_category_list=view_category_list,
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
            costs = db.session.query(Cost).filter_by(month_to_add=month).all()
        except db.exc.SQLAlchemyError:
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
            # 今月のカテゴリー別支出を取得
            costs = db.session.query(Cost).filter(Cost.month_to_add == this_month)\
                .join(CategoryPaths, Cost.category_id == CategoryPaths.descendant)\
                .filter(CategoryPaths.ancestor == cat.id)\
                .all()

            total_dict = {'category': cat.name, 'amount': sum(cost.amount for cost in costs)}
            costs_by_category.append(total_dict)
        except AttributeError:
            costs_by_category[cat] = 0
        finally:
            db.session.close()

    return costs_by_category


def _utility_costs_last_12_months(view_category_ids, months):
    # 直近12か月分の水道光熱費（各カードの折れ線ブラフ用）
    utility_costs = {}
    for month in months:
        utility_costs_per_month = {}
        for category_id in view_category_ids:
            try:
                cost = db.session.query(Cost).filter(
                    db.and_(Cost.month_to_add == month, Cost.category_id == category_id))\
                    .order_by(Cost.id).first()

                category_name = (db.session.query(Category).filter(Category.id == category_id).first()).name
                utility_costs_per_month[category_name] = cost.amount
            except AttributeError:
                utility_costs_per_month[category_name] = 0
            finally:
                db.session.close()

        utility_costs['{0:%Y-%m}'.format(month)] = utility_costs_per_month
    return utility_costs


def _insert_fixed_costs(month_to_add):
    # 固定費を取得
    try:
        fixed_costs = db.session.query(FixedCost).order_by(FixedCost.id).all()
    except db.exc.SQLAlchemyError:
        fixed_costs = {}
    finally:
        db.session.close()

    # 今月のコストを取得
    try:
        costs = db.session.query(Cost).filter_by(month_to_add=month_to_add).all()
    except db.exc.SQLAlchemyError:
        costs = {}
    finally:
        db.session.close()

    # 今月のコストにまだ固定費が入ってなければインサート
    for fc in fixed_costs:
        found = False
        for cost in costs:
            if fc.category_id == cost.category_id:
                found = True
                break

        if not found:
            now = datetime.now()

            cost = Cost()
            cost.category_id = fc.category_id
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
            except db.exc.SQLAlchemyError:
                pass
            finally:
                db.session.close()
