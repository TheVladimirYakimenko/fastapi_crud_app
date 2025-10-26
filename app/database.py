from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import (
    create_async_engine, async_sessionmaker, AsyncSession
)

from app.config import get_config, Config


config: Config = get_config()

DATABASE_URL = config.database_url

async_engine = create_async_engine(
    url=DATABASE_URL,
    echo=True
)
async_session_maker = async_sessionmaker(
    async_engine,
    expire_on_commit=False,
    class_=AsyncSession
)


class Base(DeclarativeBase):
    pass
