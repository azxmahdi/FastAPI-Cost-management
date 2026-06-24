from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config.settings import settings

DATABASE_URL = settings.DATABASE_URL
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL not found in settings or environment variables."
    )

engine = create_engine(
    DATABASE_URL, echo=True
)


Base = declarative_base()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
