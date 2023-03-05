from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from kakeibosan.views.forms import Settings
from kakeibosan.models import User, FixedCost


bp = Blueprint('settings', __name__)


@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        parameter = request.args.get('card')
        if parameter == 'add_account':
            return redirect(url_for('edit_account.edit_account', edit='add'))
        elif parameter == 'fixedcost':
            return redirect(url_for('edit_fixedcost.edit_fixedcost', edit='add'))
    else:
        users = User.query.order_by(User.id).all()
        fixed_costs = FixedCost.query.order_by(FixedCost.id)
        form = Settings()
        return render_template('settings.html', active_page='設定', fixed_costs=fixed_costs,
                               users=users, form=form)
