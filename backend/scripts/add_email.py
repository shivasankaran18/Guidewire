import asyncio
from models.database import engine
from sqlalchemy import text

async def main():
    try:
        async with engine.begin() as conn:
            print("Adding email column to workers table...")
            await conn.execute(text("ALTER TABLE workers ADD COLUMN IF NOT EXISTS email VARCHAR(320);"))
            print("Successfully added email column (or it already exists).")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
