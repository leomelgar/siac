"""Agregar columna avatar a tabla usuario

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-08-06 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6a7'
down_revision = '37b59e1b949c'   # ← Poné aquí el revision ID de la migración anterior (la de id_curso)
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('usuario', sa.Column('avatar', sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column('usuario', 'avatar')