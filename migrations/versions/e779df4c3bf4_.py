"""empty message

Revision ID: e779df4c3bf4
Revises: 31608dae688c
Create Date: 2023-05-28 17:22:00.277915

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e779df4c3bf4'
down_revision = '31608dae688c'
branch_labels = None
depends_on = None


def upgrade():
    # sqliteからMariaDBに移行後、INSERTのみできなくなった。
    # 各テーブルのidにauto_incrementを設定
    op.execute('ALTER TABLE user MODIFY id int AUTO_INCREMENT')
    op.execute('ALTER TABLE cost MODIFY id int AUTO_INCREMENT')
    op.execute('ALTER TABLE fixed_cost MODIFY id int AUTO_INCREMENT')


def downgrade():
    pass
