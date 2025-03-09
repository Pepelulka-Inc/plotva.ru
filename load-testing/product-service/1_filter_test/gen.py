# Скрипт генерирует рандомные товары и категории и загружает их в БД
import asyncpg
from dataclasses import dataclass
import uuid
import datetime
from typing import List
import string
import random
import os
import asyncio
import dotenv
import json

dotenv.load_dotenv()

# Конфиг для скрипта:
PRODUCT_COUNT=10000
CATS_COUNT=100
SELLERS_COUNT=100

MIN_PRICE=1
MAX_PRICE=1000000

POSTGRES_HOST='localhost'
POSTGRES_PORT='5432'
POSTGRES_USER=os.environ['POSTGRES_USER']
POSTGRES_PASSWORD=os.environ['POSTGRES_PASSWORD']
POSTGRES_DB=os.environ['POSTGRES_DB']

CATS_DATA='data/cats.json'
SELLERS_DATA='data/sellers.json'

@dataclass
class Product:
    product_id: uuid.UUID
    name: str
    description: str
    seller_id: uuid.UUID
    category: str
    photo_url: str
    price_rub: int
    creation_time: datetime.datetime

def gen_random_string(length: int) -> str:
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def gen_random_product(cats: List[str], sellers: List[uuid.UUID]) -> Product:
    return Product(
        product_id=uuid.uuid4(),
        name=gen_random_string(32),
        description=gen_random_string(512),
        seller_id=random.choice(sellers),
        category=random.choice(cats),
        photo_url=gen_random_string(64),
        price_rub=random.randint(MIN_PRICE, MAX_PRICE),
        creation_time=datetime.datetime(random.randint(2005,2025), random.randint(1,12), random.randint(1,28))
    )

def gen_cats():
    cats = [gen_random_string(24) for _ in range(CATS_COUNT)]
    with open(CATS_DATA, "w", encoding="utf-8") as f:
        json.dump(cats, f, indent=4)

def gen_sellers():
    cats = [str(uuid.uuid4()) for _ in range(CATS_COUNT)]
    with open(SELLERS_DATA, "w", encoding="utf-8") as f:
        json.dump(cats, f, indent=4)

def read_cats() -> List[str]:
    with open(CATS_DATA, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [str(item) for item in data]

def read_sellers() -> List[uuid.UUID]:
    with open(SELLERS_DATA, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [uuid.UUID(item) for item in data]

async def load_categories_in_pg(conn, cats: List[str]):
    query_str = 'INSERT INTO plotva.product_category (category_name) VALUES '
    for i in range(len(cats)):
        query_str += f'(${i+1})'
        if i != len(cats) - 1:
            query_str += ', '
    query_str += ';'

    await conn.execute(query_str, *cats)

async def load_product_in_pg(conn, product: Product):
    query_str = '''
INSERT INTO
    plotva.product (product_id, name, description, seller_id, category, photo_url, price_rub, creation_time)
VALUES
    ($1, $2, $3, $4, $5, $6, $7, $8);
'''
    await conn.execute(
        query_str,
        product.product_id,
        product.name,
        product.description,
        product.seller_id,
        product.category,
        product.photo_url,
        product.price_rub,
        product.creation_time,
    )

async def main():
    gen_cats()
    gen_sellers()

    cats = read_cats()
    sellers = read_sellers()

    conn = await asyncpg.connect(
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        database=POSTGRES_DB,
        host=POSTGRES_HOST,
        port=int(POSTGRES_PORT)
    )

    await load_categories_in_pg(conn, cats)

    for _ in range(PRODUCT_COUNT):
        prod = gen_random_product(cats, sellers)
        await load_product_in_pg(conn, prod)

    await conn.close()


if __name__ == '__main__':
    asyncio.run(main())

