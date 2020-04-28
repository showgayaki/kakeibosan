from flask import render_template, request, redirect, flash, url_for
from flask_login import login_required
from sqlalchemy import exc
from kakeibosan import app, db
from kakeibosan.views.forms import EditFixedCost
from kakeibosan.models import FixedCost


@app.route('/kakuninsam/settings/fixed_cost', methods=['GET', 'POST'])
@login_required
def edit_fixedcost():
    form = EditFixedCost()
    record_id = request.args.get('record_id')

    if request.method == 'POST':
        flash_category = 'info'
        if record_id:
            fixed_cost = FixedCost.query.filter_by(id=record_id).first()
            flash_message = '{}を更新しました'.format(form.sub_category.data)
        else:
            fixed_cost = FixedCost()
            flash_message = '{}を追加しました'.format(form.sub_category.data)

        fixed_cost.sub_category = form.sub_category.data
        fixed_cost.paid_to = form.paid_to.data
        fixed_cost.amount = form.amount.data
        fixed_cost.user_id = form.username.data

        try:
            db.session.add(fixed_cost)
            db.session.commit()
        except exc.SQLAlchemyError:
            flash_category = 'warning'
            flash_message = 'Insert Error'
        finally:
            db.session.close()

        flash(flash_message, flash_category)
        return redirect(url_for('settings'))
    else:
        if record_id:
            fixed_cost = FixedCost.query.filter_by(id=record_id).first()
            active_page = '固定費更新'
            form.username.default = fixed_cost.user_id
            form.process()
            form.sub_category.data = fixed_cost.sub_category
            form.paid_to.data = fixed_cost.paid_to
            form.amount.data = fixed_cost.amount
        else:
            active_page = '固定費追加'
        return render_template('edit_fixedcost.html', form=form, active_page=active_page,
                               record_id=record_id)
