from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# Async engine
engine = create_async_engine(
    settings.database_url,
    echo=False,          # Set True để debug SQL
    pool_pre_ping=True,  # Kiểm tra connection trước khi dùng
    pool_size=10,
    max_overflow=20,
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    """Base class cho tất cả SQLAlchemy models."""
    pass


async def get_db() -> AsyncSession:
    """FastAPI dependency — cấp một DB session cho mỗi request."""
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
    """Tạo tất cả bảng (dùng trong dev, production dùng Alembic)."""
    async with engine.begin() as conn:
        from app.models import document, user, workspace  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)
