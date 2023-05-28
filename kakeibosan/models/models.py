from flask_login import UserMixin
import hashlib
from datetime import datetime
from kakeibosan import db


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(100), unique=True, nullable=False)
    view_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    @classmethod
    def calculate_password_hash(cls, pw):
        return hashlib.sha512(pw.encode('utf-8')).hexdigest()

    def to_dict(self):
        user_dict = {
            'id': self.id,
            'user_name': self.user_name,
            'view_name': self.view_name,
            'email': self.email,
            'password': self.password
        }
        return user_dict


class FixedCost(db.Model):
    __tablename__ = 'fixed_cost'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(db.String(20), nullable=False)
    sub_category = db.Column(db.String(20), nullable=False)
    paid_to = db.Column(db.String(100))
    amount = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)


class Cost(db.Model):
    __tablename__ = 'cost'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    is_paid_in_advance = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(100), nullable=False)
    sub_category = db.Column(db.String(100), nullable=False)
    paid_to = db.Column(db.String(100))
    amount = db.Column(db.Integer, nullable=False)
    month_to_add = db.Column(db.Date)
    bought_in = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now())
    user_id = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        cost_dict = {
            'id': self.id,
            'is_paid_in_advance': self.is_paid_in_advance,
            'category': self.category,
            'sub_category': self.sub_category,
            'paid_to': self.paid_to,
            'amount': self.amount,
            'month_to_add': self.month_to_add,
            'bought_in': self.bought_in,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'user_id': self.user_id
        }
        return cost_dict
