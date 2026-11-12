from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .config import settings

load_dotenv()
        

"""This is for mysql setup"""
engine = create_async_engine( # create db engine, talks to database and power all query
    settings.DATABASE_URL, # db uri 
    echo=settings.DEBUG, # If DEBUG=True, SQL queries print to terminal.
    pool_pre_ping=True, #Checks if DB connection is alive before using it.
    pool_size=10, # Maximum permanent DB connections kept open.
    max_overflow=20, # Extra temporary connections allowed during heavy traffic.
)



#----session creation-----#
AsyncSessionLocal= async_sessionmaker(
    expire_on_commit=False, class_=AsyncSession,
    autoflush=False, autocommit= False, bind= engine
    )





#----------Database injection---------#
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
            

