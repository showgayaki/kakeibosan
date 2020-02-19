from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField
from wtforms.validators import DataRequired, InputRequired
from wtforms.widgets import html5
from kakeibosan.models import User


def _user():
    users = User.query.order_by(User.id)
    choices = [('', '-- 選択してください --')]
    for user in users:
        user_tuple = (user.id, user.view_name)
        choices.append(user_tuple)
    return choices


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember = BooleanField('remember')
    submit = SubmitField('Login')


class Settings(FlaskForm):
    edit_account = SubmitField('更新')
    add_account = SubmitField('新規登録')
    add_fixed_cost = SubmitField('新規登録')


class EditAccount(FlaskForm):
    username = StringField('ユーザー名', [DataRequired()])
    veiwname = StringField('表示名', [DataRequired()])
    email = StringField('email', [DataRequired()])
    password = PasswordField('パスワード', [InputRequired()])
    confirm = PasswordField('パスワード確認', [InputRequired()])
    submit = SubmitField('登録')


class EditFixedCost(FlaskForm):
    sub_category = StringField('項目', [DataRequired()])
    paid_to = StringField('支払先')
    amount = IntegerField('金額', [DataRequired()], widget=html5.NumberInput(min=1))
    username = SelectField('ユーザー名', [DataRequired()], choices=_user())
    submit = SubmitField('登録')
