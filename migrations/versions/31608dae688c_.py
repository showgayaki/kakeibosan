"""empty message

Revision ID: 31608dae688c
Revises: 1acac1fe3407
Create Date: 2023-03-07 21:35:03.240442

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '31608dae688c'
down_revision = '1acac1fe3407'
branch_labels = None
depends_on = None


def upgrade():
    """
    SQLiteでのカラム追加は、任意の位置には追加できず最後(今回だとuser_idの後ろ)に追加される。
    sub_categoryの前にcategoryを追加したいので、
    - 既存テーブルをリネーム
    - categoryを追加したテーブルを新規作成
    - リネームしたテーブルから新規作成したテーブルにデータを移行
    の手順を踏む。
    """
    op.rename_table('fixed_cost', 'fixed_cost_tmp')
    # データ移行するため、categoryのnullableはひとまずTrueにしておく
    op.create_table('fixed_cost',
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('category', sa.String(20), nullable=True),
                    sa.Column('sub_category', sa.String(20), nullable=False),
                    sa.Column('paid_to', sa.String(100)),
                    sa.Column('amount', sa.Integer, nullable=False),
                    sa.Column('user_id', sa.Integer, nullable=False),
                    )
    # fixed_cost_tmpからfixed_costへデータの移行
    op.execute('INSERT INTO fixed_cost(id, sub_category, paid_to, amount, user_id) \
               SELECT id, sub_category, paid_to, amount, user_id FROM fixed_cost_tmp'
               )
    # categoryに固定費を挿入
    op.execute('UPDATE fixed_cost SET category = "固定費"')

    # nullableをFalseに設定する
    # SQLiteは既存の列への変更に対応していないため、以下の方法で行う。
    # https://github.com/miguelgrinberg/Flask-Migrate/issues/252
    with op.batch_alter_table("fixed_cost", recreate='always') as batch_op:
        batch_op.alter_column('category', nullable=False)

    # リネームしたテーブルは削除
    op.drop_table('fixed_cost_tmp')


def downgrade():
    op.drop_column('fixed_cost', 'category')
