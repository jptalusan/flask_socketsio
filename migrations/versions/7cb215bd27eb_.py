"""empty message

Revision ID: 7cb215bd27eb
Revises: 659bfb078963
Create Date: 2018-01-30 16:12:52.447370

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7cb215bd27eb'
down_revision = '659bfb078963'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_masternode_datafile', table_name='masternode')
    op.create_index(op.f('ix_masternode_datafile'), 'masternode', ['datafile'], unique=False)
    op.drop_index('ix_slavenode_datafile', table_name='slavenode')
    op.create_index(op.f('ix_slavenode_datafile'), 'slavenode', ['datafile'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_slavenode_datafile'), table_name='slavenode')
    op.create_index('ix_slavenode_datafile', 'slavenode', ['datafile'], unique=1)
    op.drop_index(op.f('ix_masternode_datafile'), table_name='masternode')
    op.create_index('ix_masternode_datafile', 'masternode', ['datafile'], unique=1)
    # ### end Alembic commands ###
