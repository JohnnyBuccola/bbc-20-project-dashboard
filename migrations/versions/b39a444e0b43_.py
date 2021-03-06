"""empty message

Revision ID: b39a444e0b43
Revises: 80daa4746e25
Create Date: 2021-10-20 14:09:41.006903

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b39a444e0b43'
down_revision = '80daa4746e25'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('projects', sa.Column('project_status', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('projects', 'project_status')
    # ### end Alembic commands ###
