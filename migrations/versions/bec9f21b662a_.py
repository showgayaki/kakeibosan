"""empty message

Revision ID: bec9f21b662a
Revises: e779df4c3bf4
Create Date: 2023-06-02 08:38:44.390322

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'bec9f21b662a'
down_revision = 'e779df4c3bf4'
branch_labels = None
depends_on = None

TABLE_LIST = ['cost', 'fixed_cost']


def upgrade():
    op.execute('DROP TABLE IF EXISTS category_paths')
    op.execute('DROP TABLE IF EXISTS category')

    category = op.create_table('category',
                               sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                               sa.Column('name', sa.String(length=100), nullable=False),
                               sa.Column('in_english', sa.String(length=100), nullable=True),
                               sa.Column('chart_color', sa.String(length=100), nullable=True),
                               sa.PrimaryKeyConstraint('id')
                               )
    category_paths = op.create_table('category_paths',
                                     sa.Column('ancestor', sa.Integer(), nullable=False),
                                     sa.Column('descendant', sa.Integer(), nullable=False),
                                     sa.ForeignKeyConstraint(['ancestor'], ['category.id'], ),
                                     sa.ForeignKeyConstraint(['descendant'], ['category.id'], ),
                                     sa.PrimaryKeyConstraint('ancestor', 'descendant')
                                     )
    # データ挿入
    op.bulk_insert(category,
                   [
                       # 固定費
                       {'name': '固定費', 'in_english': None, 'chart_color': None},
                       {'name': '家賃', 'in_english': None, 'chart_color': None},
                       {'name': '管理費', 'in_english': None, 'chart_color': None},
                       {'name': '手数料', 'in_english': None, 'chart_color': None},
                       {'name': '更新料', 'in_english': None, 'chart_color': None},
                       {'name': '駐輪場', 'in_english': None, 'chart_color': None},
                       # 光熱費
                       {'name': '光熱費', 'in_english': None, 'chart_color': None},
                       {'name': '電気代', 'in_english': 'ElectricCharge', 'chart_color': 'rgb(255, 21, 51)'},
                       {'name': 'ガス代', 'in_english': 'GasCharge', 'chart_color': 'rgb(255, 163, 0)'},
                       {'name': '水道代', 'in_english': 'WaterCharge', 'chart_color': 'rgb(0, 106, 182)'},
                       # 食費
                       {'name': '食費', 'in_english': None, 'chart_color': None},
                       {'name': '食材費', 'in_english': None, 'chart_color': None},
                       {'name': '外食費', 'in_english': None, 'chart_color': None},
                       # 日用品
                       {'name': '日用品', 'in_english': None, 'chart_color': None},
                       {'name': '日用品', 'in_english': None, 'chart_color': None},
                       {'name': '洗剤類', 'in_english': None, 'chart_color': None},
                       # 交通費
                       {'name': '交通費', 'in_english': None, 'chart_color': None},
                       {'name': 'タイムズ', 'in_english': None, 'chart_color': None},
                       {'name': 'レンタカー', 'in_english': None, 'chart_color': None},
                       {'name': 'ガソリン代', 'in_english': None, 'chart_color': None},
                   ]
                   )
    op.bulk_insert(category_paths,
                   [
                       # 固定費
                       {'ancestor': 1, 'descendant': 1},  # 固定費
                       {'ancestor': 1, 'descendant': 2},  # 家賃
                       {'ancestor': 1, 'descendant': 3},  # 管理費
                       {'ancestor': 1, 'descendant': 4},  # 手数料
                       {'ancestor': 1, 'descendant': 5},  # 駐輪場
                       {'ancestor': 1, 'descendant': 6},  # 手数料
                       # 光熱費
                       {'ancestor': 7, 'descendant': 7},  # 光熱費
                       {'ancestor': 7, 'descendant': 8},  # 電気代
                       {'ancestor': 7, 'descendant': 9},  # ガス代
                       {'ancestor': 7, 'descendant': 10},  # 水道代
                       # 食費
                       {'ancestor': 11, 'descendant': 11},  # 食費
                       {'ancestor': 11, 'descendant': 12},  # 食材費
                       {'ancestor': 11, 'descendant': 13},  # 外食費
                       # 日用品
                       {'ancestor': 14, 'descendant': 14},  # 日用品
                       {'ancestor': 14, 'descendant': 15},  # 日用品
                       {'ancestor': 14, 'descendant': 16},  # 洗剤類
                       # 交通費
                       {'ancestor': 17, 'descendant': 17},  # 交通費
                       {'ancestor': 17, 'descendant': 18},  # タイムズ
                       {'ancestor': 17, 'descendant': 19},  # レンタカー
                       {'ancestor': 17, 'descendant': 20},  # ガソリン代
                   ])

    # 同じwithの中だとエラーが発生したので、処理を分けた
    for table in TABLE_LIST:
        with op.batch_alter_table(table, schema=None, recreate='always') as batch_op:
            # カラム作成、いったんnullableはTrue
            batch_op.add_column(sa.Column('category_id', sa.Integer(), default=None, nullable=True), insert_before='paid_to')
        with op.batch_alter_table(table, schema=None, recreate='always') as batch_op:
            # データ挿入
            batch_op.execute(f'UPDATE {table}, category SET {table}.category_id = category.id WHERE {table}.sub_category = category.name')
            # リレーション設定
            batch_op.create_foreign_key(f'{table}_category_id', 'category', ['category_id'], ['id'])
            batch_op.create_foreign_key(f'{table}_user_id', 'user', ['user_id'], ['id'])
            # いらなくなったカラム削除
            batch_op.drop_column('category')
            batch_op.drop_column('sub_category')
            # nullableをFalseにする
            batch_op.alter_column('category_id', nullable=False)


def downgrade():
    for table in TABLE_LIST:
        # 外部キー制約削除
        op.execute(f'ALTER TABLE {table} DROP CONSTRAINT {table}_category_id')
        op.execute(f'ALTER TABLE {table} DROP CONSTRAINT {table}_user_id')

        with op.batch_alter_table(table, schema=None, recreate='always') as batch_op:
            # 削除したカラムを戻す
            batch_op.add_column(sa.Column('sub_category', mysql.VARCHAR(length=100), nullable=True), insert_before='paid_to')
            batch_op.add_column(sa.Column('category', mysql.VARCHAR(length=100), nullable=True), insert_before='sub_category')
        with op.batch_alter_table(table, schema=None, recreate='always') as batch_op:
            # サブカテゴリーを元に戻す
            batch_op.execute(f'UPDATE {table}, category SET {table}.sub_category = category.name WHERE {table}.category_id = category.id')
            # カテゴリーを元に戻す
            batch_op.execute(f'UPDATE {table}, category, category_paths SET {table}.category = category.name WHERE category.id = (SELECT ancestor FROM category_paths WHERE {table}.category_id = descendant)')
        # 前バージョンにはなかったカラム削除
        op.drop_column(table, 'category_id')

    # 前バージョンにはなかったテーブル削除
    op.drop_table('category_paths')
    op.drop_table('category')
