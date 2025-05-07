import pandas as pd
import asyncio
from backend.app.db.database import AsyncSessionLocal, engine
from backend.app.models import models

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

async def load_users():
    df = pd.read_csv("data/users.csv")

    async with AsyncSessionLocal() as session:
        async with session.begin():
            for _, row in df.iterrows():
                user = models.User(
                    user_id=row["user_id"],
                    name=row["name"],
                    email=row["email"],
                    password=row["password"]
                )
                await session.merge(user)
        await session.commit()
        


async def main():
    await create_tables()
    await load_users()

if __name__ == "__main__":
    asyncio.run(main())
