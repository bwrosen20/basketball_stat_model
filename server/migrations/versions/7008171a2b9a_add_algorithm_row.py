"""Add algorithm row

Revision ID: 7008171a2b9a
Revises: 5273d2c177bc
Create Date: 2024-02-06 15:28:09.014781

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7008171a2b9a'
down_revision = '5273d2c177bc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('final_bet', sa.Column('algorithm', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('final_bet', 'algorithm')
    # ### end Alembic commands ###
