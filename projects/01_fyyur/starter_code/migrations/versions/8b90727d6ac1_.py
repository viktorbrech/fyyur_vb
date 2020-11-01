"""empty message

Revision ID: 8b90727d6ac1
Revises: 1b82009c6a19
Create Date: 2020-10-23 19:20:54.607915

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8b90727d6ac1'
down_revision = '1b82009c6a19'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('seeking_venue', sa.Boolean(), nullable=True))
    op.add_column('Artist', sa.Column('website_link', sa.String(length=120), nullable=True))
    op.add_column('Venue', sa.Column('genres', sa.String(length=120), nullable=True))
    op.add_column('Venue', sa.Column('seeking_talent', sa.Boolean(), nullable=True))
    op.add_column('Venue', sa.Column('website_link', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'website_link')
    op.drop_column('Venue', 'seeking_talent')
    op.drop_column('Venue', 'genres')
    op.drop_column('Artist', 'website_link')
    op.drop_column('Artist', 'seeking_venue')
    # ### end Alembic commands ###