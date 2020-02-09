from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField
from wtforms.validators import DataRequired, InputRequired
from wtforms.widgets import Select, HTMLString, html_params, html5
from kakeibosan.models import User


def _render_kw():
    return {"data-style": "text-dark bg-white border h6 font-weight-normal"}


def _user():
    users = User.query.filter(User.id > 1).order_by(User.id)
    choices = [('', '-- 選択してください --')]
    for user in users:
        user_tuple = (user.id, user.view_name)
        choices.append(user_tuple)
    return choices


# WTForms.widgets.Selectを拡張
class SelectHasAttributesOption(Select):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        if self.multiple:
            kwargs['multiple'] = True
        if 'required' not in kwargs and 'required' in getattr(field, 'flags', []):
            kwargs['required'] = True
        html = ['<select %s>' % html_params(name=field.name, **kwargs)]
        for val, label, selected, render_kw in field.iter_choices_with_render_kw():
            html.append(self.render_option(val, label, selected, **render_kw))
        html.append('</select>')
        return HTMLString(''.join(html))


# WTForms.SelectFieldを拡張
class SelectHasAttributesOptionField(SelectField):
    widget = SelectHasAttributesOption()

    def iter_choices(self):
        for value, label, *_ in self.choices:
            yield value, label, self.coerce(value) == self.data

    def pre_validate(self, form):
        for v, *_ in self.choices:
            if self.data == v:
                break
        else:
            raise ValueError(self.gettext('Not a valid choice'))

    def iter_choices_with_render_kw(self):
        for value, label, *render_kw in self.choices:
            render_kw = render_kw[0] if render_kw else {}
            yield value, label, self.coerce(value) == self.data, render_kw


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
    username = SelectField('ユーザー名', [DataRequired()], render_kw=_render_kw(), choices=_user())
    submit = SubmitField('登録')
