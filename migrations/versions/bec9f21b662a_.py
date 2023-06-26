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
                               sa.Column('id', sa.Integer(), autoincrement=False, nullable=False),
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
                       {'id': 100, 'name': '固定費', 'in_english': None, 'chart_color': None},
                       {'id': 101, 'name': '家賃', 'in_english': None, 'chart_color': None},
                       {'id': 102, 'name': '管理費', 'in_english': None, 'chart_color': None},
                       {'id': 103, 'name': '手数料', 'in_english': None, 'chart_color': None},
                       {'id': 104, 'name': '更新料', 'in_english': None, 'chart_color': None},
                       {'id': 105, 'name': '駐輪場', 'in_english': None, 'chart_color': None},
                       # 光熱費
                       {'id': 200, 'name': '光熱費', 'in_english': None, 'chart_color': None},
                       {'id': 201, 'name': '電気代', 'in_english': 'ElectricCharge', 'chart_color': 'rgb(255, 21, 51)'},
                       {'id': 202, 'name': 'ガス代', 'in_english': 'GasCharge', 'chart_color': 'rgb(255, 163, 0)'},
                       {'id': 203, 'name': '水道代', 'in_english': 'WaterCharge', 'chart_color': 'rgb(0, 106, 182)'},
                       # 食費
                       {'id': 300, 'name': '食費', 'in_english': None, 'chart_color': None},
                       {'id': 301, 'name': '食材費', 'in_english': None, 'chart_color': None},
                       {'id': 302, 'name': '外食費', 'in_english': None, 'chart_color': None},
                       # 日用品
                       {'id': 400, 'name': '日用品', 'in_english': None, 'chart_color': None},
                       {'id': 401, 'name': '日用品', 'in_english': None, 'chart_color': None},
                       {'id': 402, 'name': '洗剤類', 'in_english': None, 'chart_color': None},
                       # 交通費
                       {'id': 500, 'name': '交通費', 'in_english': None, 'chart_color': None},
                       {'id': 501, 'name': 'タイムズ', 'in_english': None, 'chart_color': None},
                       {'id': 502, 'name': 'レンタカー', 'in_english': None, 'chart_color': None},
                       {'id': 503, 'name': 'ガソリン代', 'in_english': None, 'chart_color': None},
                   ]
                   )
    op.bulk_insert(category_paths,
                   [
                       # 固定費
                       {'ancestor': 100, 'descendant': 100},  # 固定費
                       {'ancestor': 100, 'descendant': 101},  # 家賃
                       {'ancestor': 100, 'descendant': 102},  # 管理費
                       {'ancestor': 100, 'descendant': 103},  # 手数料
                       {'ancestor': 100, 'descendant': 104},  # 駐輪場
                       {'ancestor': 100, 'descendant': 105},  # 手数料
                       # 光熱費
                       {'ancestor': 200, 'descendant': 200},  # 光熱費
                       {'ancestor': 200, 'descendant': 201},  # 電気代
                       {'ancestor': 200, 'descendant': 202},  # ガス代
                       {'ancestor': 200, 'descendant': 203},  # 水道代
                       # 食費
                       {'ancestor': 300, 'descendant': 300},  # 食費
                       {'ancestor': 300, 'descendant': 301},  # 食材費
                       {'ancestor': 300, 'descendant': 302},  # 外食費
                       # 日用品
                       {'ancestor': 400, 'descendant': 400},  # 日用品
                       {'ancestor': 400, 'descendant': 401},  # 日用品
                       {'ancestor': 400, 'descendant': 402},  # 洗剤類
                       # 交通費
                       {'ancestor': 500, 'descendant': 500},  # 交通費
                       {'ancestor': 500, 'descendant': 501},  # タイムズ
                       {'ancestor': 500, 'descendant': 502},  # レンタカー
                       {'ancestor': 500, 'descendant': 503},  # ガソリン代
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
