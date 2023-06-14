"""Access_history partioning

Revision ID: f85d9ce79a73
Revises: 02449c4f845b
Create Date: 2023-06-14 14:42:33.792986

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f85d9ce79a73'
down_revision = '02449c4f845b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE TABLE IF NOT EXISTS access_history_new
    (
        id UUID NOT NULL,
        user_id UUID NOT NULL,
        action character varying(128) NOT NULL,
        created timestamp without time zone NOT NULL,
        user_agent character varying(256),
        CONSTRAINT access_history_new_pkey PRIMARY KEY (id, created)
    ) PARTITION BY RANGE (created);

    CREATE TABLE IF NOT EXISTS access_history_y2022 
    PARTITION OF access_history_new
    FOR VALUES FROM ('2022-01-01') TO ('2023-01-01');

    CREATE TABLE IF NOT EXISTS access_history_y2023 
    PARTITION OF access_history_new
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');

    CREATE TABLE IF NOT EXISTS access_history_y2024 
    PARTITION OF access_history_new
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

    INSERT INTO access_history_new SELECT * FROM access_history;

    ALTER TABLE access_history RENAME TO access_history_old;
    ALTER TABLE access_history_new RENAME TO access_history;

    DROP TABLE IF EXISTS access_history_old;
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE access_history RENAME TO access_history_new;
        ALTER TABLE access_history_old RENAME TO access_history;

        DROP TABLE IF EXISTS access_history_y2024;
        DROP TABLE IF EXISTS access_history_y2023;
        DROP TABLE IF EXISTS access_history_new;
    """)
