import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

from src.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def wait_for_db():
    """Wait for database to be ready."""
    retries = 0
    max_retries = 30
    
    url = settings.SQLALCHEMY_DATABASE_URI
    engine = create_async_engine(url)

    while retries < max_retries:
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("Database is ready!")
            return
        except Exception as e:
            retries += 1
            logger.warning(f"Database not ready yet ({retries}/{max_retries}). Error: {e}")
            await asyncio.sleep(1)
    
    raise Exception("Could not connect to database")

if __name__ == "__main__":
    asyncio.run(wait_for_db())
