"""citizens table

Revision ID: 5f45636e7d42
Revises: 3580c7994661
Create Date: 2019-08-18 15:35:45.726287

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5f45636e7d42'
down_revision = '3580c7994661'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'citizens', 'imports', ['import_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'citizens', type_='foreignkey')
    # ### end Alembic commands ###
