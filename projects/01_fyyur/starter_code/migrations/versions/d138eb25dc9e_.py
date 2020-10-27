"""empty message

Revision ID: d138eb25dc9e
Revises: 3c135fa5f492
Create Date: 2020-10-27 12:00:13.001774

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd138eb25dc9e'
down_revision = '3c135fa5f492'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('seeking_venue_message', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'seeking_venue_message')
    # ### end Alembic commands ###
