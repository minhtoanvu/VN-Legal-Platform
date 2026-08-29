from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

import sys
from sqlalchemy.pool import NullPool

# Tự động dùng NullPool khi chạy pytest để tránh lỗi "Event loop is closed"
db_kwargs = {
    "echo": False,
    "pool_pre_ping": True,
    "connect_args": {
        "command_timeout": 5,
        "timeout": 5
    }
}
if "pytest" in sys.modules:
    db_kwargs["poolclass"] = NullPool
else:
    db_kwargs["pool_size"] = 10
    db_kwargs["max_overflow"] = 20

engine = create_async_engine(
    settings.database_url,
    **db_kwargs
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    async with engine.begin() as conn:
        from app.models import document, user, workspace  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)
