import asyncio
import json
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import insert
from backend.app.db.database import AsyncSessionLocal
from backend.app.models import models
from datetime import datetime

df = pd.read_csv("data/walmart-products.csv")

#Writing a function to clean the data
def clean_data(row):
    def safe_json(value):
        try:
            return json.loads(value) if pd.notna(value) else None
        except:
            return None
        
    #Also, rating_stars is in JSON, we need a weighted average and turn it to float
    def weighted_average(ratings_data):
        try:
            ratings = json.loads(ratings_data)
            total_votes = sum(ratings.get(key, 0) for key in ratings)
            if total_votes == 0:
                return None
            weighted_sum = sum(int(key.split("_")[0]) * ratings[key] for key in ratings)
            return round(weighted_sum / total_votes, 2)
        except:
            return None

    name = row.get("product_name", "N/A")
    category = json.loads(row["categories"])[0] if pd.notna(row["categories"]) else None
    description = row.get("description", None)
    price = float(row["initial_price"]) if pd.notna(row["initial_price"]) else None
    final_price = float(row["final_price"]) if pd.notna(row["final_price"]) else None
    brand = row.get("brand", "")
    discount = row.get("discount", None)
    currency = row.get("currency", None)
    image_url = json.loads(row["image_urls"])[0] if pd.notna(row["image_urls"]) else None
    image_urls = safe_json(row.get("image_urls"))
    rating_stars = weighted_average(row.get("rating_stars"))
    sizes = safe_json(row.get("sizes"))
    colors = safe_json(row.get("colors"))
    seller = row.get("seller", None)
    top_reviews = safe_json(row.get("top_reviews"))
    categories = safe_json(row.get("categories"))

    try:
        timestamp = pd.to_datetime(row["timestamp"]) if pd.notna(row["timestamp"]) else None
    except Exception as e:
        timestamp = None
    if price is None or timestamp is None:
        return None 

    # Returning clean data as a dict
    return {
        "name": name,
        "category": category,
        "description": description,
        "price": price,
        "final_price": final_price,
        "brand": brand,
        "discount": discount,
        "currency": currency,
        "image_url": image_url,
        "image_urls": image_urls,
        "rating_stars": rating_stars,
        "sizes": sizes,
        "colors": colors,
        "seller": seller,
        "top_reviews": top_reviews,
        "categories": categories,
        "timestamp": timestamp,
    }

#loading the data into the database using the function
async def load_products():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            for _, row in df.iterrows():
                product_data = clean_data(row)

                if not isinstance(product_data, dict):
                    print(f"Invalid product data: {product_data}")
                    continue

                if not product_data or product_data['price'] is None or product_data['timestamp'] is None:
                    continue

                query = insert(models.Product).values(**product_data).on_conflict_do_nothing(index_elements=['id'])
                await session.execute(query)
            await session.commit() 
            print("Products loaded successfully!")

async def main():
    await load_products()

if __name__ == "__main__":
    asyncio.run(main())