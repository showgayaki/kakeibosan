from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_required
from kakeibosan import db
from kakeibosan.views.forms import SettingsAccount
from kakeibosan.models import User


bp = Blueprint('settings_account', __name__)


@bp.route('/settings/account', methods=['GET', 'POST'])
@login_required
def settings_account():
    form = SettingsAccount()
    record_id = request.args.get('record_id')
    user = User.query.filter_by(id=record_id).first()
    active_page = ''

    if request.method == 'POST':
        if form.password.data == form.confirm.data:
            flash_category = 'info'
            password = User.calculate_password_hash(form.password.data)
            if record_id:
                flash_message = '{}を更新しました'.format(form.username.data)
            else:
                user = User()
                flash_message = '{}を追加しました'.format(form.username.data)

            user.user_name = form.username.data
            user.view_name = form.veiwname.data
            user.email = form.email.data
            user.password = password

            try:
                db.session.add(user)
                db.session.commit()
            except db.exc.SQLAlchemyError:
                flash_category = 'warning'
                flash_message = 'Insert Error'
            finally:
                db.session.close()

            flash(flash_message, flash_category)
            return redirect(url_for('settings.settings'))
        else:
            flash('パスワードが一致しません', 'warning')
    else:
        if record_id:
            active_page = 'ユーザー更新'
            form.username.data = user.user_name
            form.veiwname.data = user.view_name
            form.email.data = user.email
        else:
            active_page = 'ユーザー追加'
    return render_template('settings_account.html', active_page=active_page, form=form, record_id=record_id)
