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
        view_category = db.session.query(Category).filter(Category.chart_color != None).all()  # noqa: E711

        view_category_ids = []
        view_category_list = []
        for vc in view_category:
            view_category_ids.append(vc.id)
            view_category_list.append(vc.to_dict())
    except db.exc.SQLAlchemyError:
        category_parent = None
    finally:
        db.session.close()

    this_year = datetime.today().year
    last_year = this_year - 1
    # ダッシュボード一番上の大きい折れ線グラフ用
    total_costs_this_year = _yearly_costs(this_year)
    total_costs_last_year = _yearly_costs(last_year)
    # 当月の出費割合円グラフ用
    costs_this_month_by_category = _costs_this_month_by_category(this_month, category_parent)
    # 光熱費折れ線グラフ用
    utility_this_year = _utility_costs_yearly(this_year, view_category_ids)
    utility_last_year = _utility_costs_yearly(last_year, view_category_ids)

    return render_template(
        'dashboard.html',
        active_page='ダッシュボード',
        this_month=this_month,
        total_costs_last_year=total_costs_last_year,
        total_costs_this_year=total_costs_this_year,
        costs_this_month_by_category=costs_this_month_by_category,
        utility_this_year=utility_this_year,
        utility_last_year=utility_last_year,
        view_category_list=view_category_list,
    )


def _yearly_costs(year):
    """指定年の 1〜12 月の合計を返す"""
    months = []
    totals = []
    for m in range(1, 13):
        first_day = datetime(year, m, 1).date()
        months.append(f'{m}月')
        try:
            costs = db.session.query(Cost).filter(
                Cost.month_to_add == first_day
            ).all()
        except db.exc.SQLAlchemyError:
            costs = []
        finally:
            db.session.close()
        totals.append(sum(c.amount for c in costs))
    return {'year': year, 'months': months, 'totals': totals}


def _utility_costs_yearly(year, category_ids):
    result = {cid: [] for cid in category_ids}
    months = [f"{m}月" for m in range(1, 13)]
    for m in range(1, 13):
        first_day = datetime(year, m, 1).date()
        for cid in category_ids:
            try:
                cost = db.session.query(Cost).filter(
                    db.and_(Cost.month_to_add == first_day,
                            Cost.category_id == cid)
                ).order_by(Cost.id).first()
                amount = cost.amount if cost else 0
            except Exception:
                amount = 0
            finally:
                db.session.close()
            result[cid].append(amount)
    return {"year": year, "months": months, "totals": result}


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
