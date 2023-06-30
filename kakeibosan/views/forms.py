import re
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField, widgets
from wtforms.validators import DataRequired, EqualTo, ValidationError, Length
from kakeibosan import db
from kakeibosan.models import User, Category, CategoryPaths


class CustomRegexp(object):
    """
    Regexpが効かない。プルリクはあるが、まだ反映されてないみたい。
    なので自分で追加。
    https://github.com/wtforms/wtforms/pull/759/commits/b86c6256d29418c35ca6e4b849756776da0b9227
    """
    def __init__(self, regex, flags=0, message=None):
        if isinstance(regex, str):
            regex = re.compile(regex, flags)
        self.regex = regex
        self.message = message
        # 追加
        self.field_flags = {'pattern': regex.pattern}

    def __call__(self, form, field, message=None):
        match = self.regex.match(field.data or "")
        if match:
            return match

        if message is None:
            if self.message is None:
                message = field.gettext("Invalid input.")
            else:
                message = self.message

        raise ValidationError(message)


class LoginForm(FlaskForm):
    username = StringField('username', [DataRequired()])
    password = PasswordField('password', [DataRequired()])
    remember = BooleanField('remember')
    submit = SubmitField('Login')


class SettingsAccount(FlaskForm):
    username = StringField('ユーザー名', [DataRequired()])
    veiwname = StringField('表示名', [DataRequired()])
    email = StringField('email', [DataRequired()])
    password = PasswordField('パスワード', [DataRequired(), EqualTo('confirm', message='パスワードが一致しません')])
    confirm = PasswordField('パスワード確認', [DataRequired()])
    submit = SubmitField('登録')


class SettingsCagegory(FlaskForm):
    category = StringField('種別', [DataRequired()])
    category_select = SelectField('種別', [DataRequired()], default=0)
    subcategory = StringField('種別', [DataRequired()])
    subcategory_select = SelectField('項目', [DataRequired()], default=0)
    in_english = StringField('英語名')
    chart_color = StringField('チャートカラー', [CustomRegexp('^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$')])
    color_picker = StringField('カラーピッカー', widget=widgets.ColorInput())
    submit = SubmitField('登録')

    def __init__(self, *args, **kwargs):
        super(SettingsCagegory, self).__init__(*args, **kwargs)
        self.choices = [('', '-- 選択してください --')]

        self.category_select.choices = self.category_choices()
        self.subcategory_select.choices = self.subcategory_choices()

    def category_choices(self):
        categories = db.session.query(
            Category.id,
            Category.name
        ).join(CategoryPaths, Category.id == CategoryPaths.descendant)\
         .filter(CategoryPaths.ancestor == CategoryPaths.descendant)\
         .order_by(Category.id)

        choices = self.choices + [(category.id, category.name) for category in categories]
        return choices

    def subcategory_choices(self):
        categories = db.session.query(
            CategoryPaths.ancestor,
            Category.id,
            Category.name
        ).join(CategoryPaths, Category.id == CategoryPaths.descendant)\
         .filter(CategoryPaths.ancestor != CategoryPaths.descendant)\
         .order_by(Category.id)

        # <option value="1-3">管理費</option> という形にする
        # とりあえずoptionにはすべてのsubcategoryを入れておいて、
        # 選択されたcategoryによっての表示・非表示はJavaScript側でやる
        choices = self.choices + [('{}-{}'.format(category.ancestor, category.id), category.name) for category in categories]
        return choices


class SettingsFixedCost(FlaskForm):
    category_select = SelectField('種別', [DataRequired()], default=0)
    subcategory_select = SelectField('項目', [DataRequired()], default=0)
    paid_to = StringField('支払先')
    amount = IntegerField('金額', [DataRequired()], widget=widgets.NumberInput(min=0))
    username = SelectField('ユーザー名', [DataRequired()], default=0)
    submit = SubmitField('登録')

    def __init__(self, *args, **kwargs):
        super(SettingsFixedCost, self).__init__(*args, **kwargs)
        self.choices = [('', '-- 選択してください --')]

        self.category_select.choices = self.category_choices()
        self.subcategory_select.choices = self.subcategory_choices()
        self.username.choices = self.user_choices()

    def category_choices(self):
        categories = db.session.query(
            Category.id,
            Category.name
        ).join(CategoryPaths, Category.id == CategoryPaths.descendant)\
         .filter(CategoryPaths.ancestor == CategoryPaths.descendant)\
         .order_by(Category.id)

        choices = self.choices + [(category.id, category.name) for category in categories]
        return choices

    def subcategory_choices(self):
        categories = db.session.query(
            CategoryPaths.ancestor,
            Category.id,
            Category.name
        ).join(CategoryPaths, Category.id == CategoryPaths.descendant)\
         .filter(CategoryPaths.ancestor != CategoryPaths.descendant)\
         .order_by(Category.id)

        # <option value="1-3">管理費</option> という形にする
        # とりあえずoptionにはすべてのsubcategoryを入れておいて、
        # 選択されたcategoryによっての表示・非表示はjacascript側でやる
        choices = self.choices + [('{}-{}'.format(category.ancestor, category.id), category.name) for category in categories]
        return choices

    def user_choices(self):
        users = db.session.query(User).order_by(User.id)
        choices = self.choices + [(user.id, user.view_name) for user in users]
        return choices
