from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField
from wtforms.validators import DataRequired, InputRequired
from wtforms import widgets
from kakeibosan import db
from kakeibosan.models import User, Category, CategoryPaths


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember = BooleanField('remember')
    submit = SubmitField('Login')


class Settings(FlaskForm):
    add_fixed_cost = SubmitField('新規登録')


class EditAccount(FlaskForm):
    username = StringField('ユーザー名', [DataRequired()])
    veiwname = StringField('表示名', [DataRequired()])
    email = StringField('email', [DataRequired()])
    password = PasswordField('パスワード', [InputRequired()])
    confirm = PasswordField('パスワード確認', [InputRequired()])
    submit = SubmitField('登録')


class EditFixedCost(FlaskForm):
    category = SelectField('種別', [DataRequired()], default=0)
    subcategory = SelectField('項目', [DataRequired()], default=0)
    paid_to = StringField('支払先')
    amount = IntegerField('金額', [DataRequired()], widget=widgets.NumberInput(min=0))
    username = SelectField('ユーザー名', [DataRequired()], default=0)
    submit = SubmitField('登録')

    def __init__(self, *args, **kwargs):
        super(EditFixedCost, self).__init__(*args, **kwargs)
        self.choices = [('', '-- 選択してください --')]

        self.category.choices = self.category_choices()
        self.subcategory.choices = self.subcategory_choices()
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
