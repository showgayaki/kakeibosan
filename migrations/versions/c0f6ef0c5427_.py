"""empty message

Revision ID: c0f6ef0c5427
Revises: bec9f21b662a
Create Date: 2023-07-01 10:59:11.796846

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c0f6ef0c5427'
down_revision = 'bec9f21b662a'
branch_labels = None
depends_on = None


def upgrade():
    new_value = {
        101: 'Rent', 102: 'MaintenanceFee', 103: 'Commission', 104: 'RenewalFee', 105: 'BicycleParkingFee',
        301: 'FoodCost', 302: 'EatingOutCost',
        401: 'DailyNecessaries', 402: 'Detergent',
        501: 'TimesCarShare', 502: 'RentalCar', 503: 'GasolineFee',
    }

    for key, val in new_value.items():
        op.execute(f'UPDATE category SET in_english = "{val}" WHERE id = {key}')


def downgrade():
    downgrade_ids = [
        101, 102, 103, 104, 105,
        301, 302,
        401, 402,
        501, 502, 503,
    ]

    for i in downgrade_ids:
        op.execute(f'UPDATE category SET in_english = NULL WHERE id = {i}')
