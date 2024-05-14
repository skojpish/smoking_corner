from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

DB_URL = f"sqlite+aiosqlite:///sqlite3.db"

engine = create_async_engine(DB_URL)

async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

