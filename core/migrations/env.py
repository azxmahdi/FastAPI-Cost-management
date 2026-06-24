import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv
from pathlib import Path

from config.database import Base
from account.models import UserModel, RefreshTokenModel
from cost.models import CostModel

env_file_path = Path(__file__).parent.parent.joinpath("envs", "dev", ".env")

load_dotenv(dotenv_path=env_file_path)

database_url_from_env = os.getenv("DATABASE_URL")

if not database_url_from_env:
    if not env_file_path.exists():
        raise FileNotFoundError(f".env file not found at {env_file_path}. Please ensure it is in the correct location.")
    else:
        raise ValueError(f"DATABASE_URL not found in {env_file_path} or environment variables.")



config = context.config
fileConfig(config.config_file_name)


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        url=database_url_from_env, # URL از .env
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=Base.metadata,
            render_as_batch=True
        )
        with context.begin_transaction():
            context.run_migrations()

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=database_url_from_env, # URL از .env
        target_metadata=Base.metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "fixed"},
        render_as_batch=True
    )
    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

