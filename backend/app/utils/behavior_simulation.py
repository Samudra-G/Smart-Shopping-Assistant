import asyncio
import random
from datetime import datetime, timedelta, timezone
from sqlalchemy import insert
from sqlalchemy.future import select
from backend.app.db.database import AsyncSessionLocal
from backend.app.models import models

NUMBER_OF_EVENTS = 100

#We will use this function to simulate the behavior of users purchasing, browsing products or add to cart
async def user_behaviour_simulation():
    async with AsyncSessionLocal() as session:
        query1 = await session.execute(select(models.User))
        query2 = await session.execute(select(models.Product))

        users = query1.scalars().all()
        products = query2.scalars().all()

        if not users or not products:
            print("No users or products found in the database.")
            return

        for _ in range(NUMBER_OF_EVENTS):
            user = random.choice(users)
            product = random.choice(products)

            #Browsing
            browsing_entry = insert(models.BrowsingHistory).values(
                user_id=user.user_id,
                product_id=product.id,
                viewed_at=datetime.now(timezone.utc) - timedelta(minutes=random.randint(0, 1000))
            )
            await session.execute(browsing_entry)

            #Cart entry
            if random.random() < 0.6:
                quantity = random.randint(1, 3)
                cart_entry = insert(models.CartItem).values(
                    user_id=user.user_id,
                    product_id=product.id,
                    quantity=quantity,
                    added_at=datetime.now(timezone.utc) - timedelta(minutes=random.randint(0, 500))
                )

                await session.execute(cart_entry)

                #purchase after adding to cart
                if random.random() < 0.4:
                    purchase_entry = insert(models.Purchase).values(
                        user_id=user.user_id,
                        product_id=product.id,
                        purchased_at=datetime.now(timezone.utc) - timedelta(minutes=random.randint(0, 500))
                    )
                    await session.execute(purchase_entry)
            #Case for direct purchase
            elif random.random() < 0.3:
                purchase_entry = insert(models.Purchase).values(
                    user_id=user.user_id,
                    product_id=product.id,
                    purchased_at=datetime.now(timezone.utc) - timedelta(minutes=random.randint(0, 500))
                )
                await session.execute(purchase_entry)

        await session.commit()
        print("User behavior simulation completed successfully.")

#Main function to run the simulation
async def main():
    await user_behaviour_simulation()

if __name__ == "__main__":
    asyncio.run(main())