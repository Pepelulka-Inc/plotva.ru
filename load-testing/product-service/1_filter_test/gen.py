# Скрипт генерирует рандомные товары и категории и загружает их в БД
import asyncpg
from dataclasses import dataclass
import uuid
import datetime
from typing import List
import string
import random
import asyncio
import os
import dotenv
import json
from pathlib import Path

dotenv.load_dotenv()

# Конфиг для скрипта:
PRODUCTS_COUNT = 10000
CATEGORIES_COUNT = 100
SELLERS_COUNT = 100

MIN_PRICE = 1
MAX_PRICE = 1000000

POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5432"
POSTGRES_USER = os.environ["POSTGRES_USER"]
POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
POSTGRES_DB = os.environ["POSTGRES_DB"]

CATEGORIES_DATA_PATH = Path("data/categories.json")
SELLERS_DATA_PATH = Path("data/sellers.json")


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
    return "".join(random.choice(characters) for _ in range(length))


def gen_random_product(categories: List[str], sellers: List[uuid.UUID]) -> Product:
    return Product(
        product_id=uuid.uuid4(),
        name=gen_random_string(32),
        description=gen_random_string(512),
        seller_id=random.choice(sellers),
        category=random.choice(categories),
        photo_url=gen_random_string(64),
        price_rub=random.randint(MIN_PRICE, MAX_PRICE),
        creation_time=datetime.datetime(
            random.randint(2005, 2025), random.randint(1, 12), random.randint(1, 28)
        ),
    )


def gen_random_products(
    categories: List[str], sellers: List[uuid.UUID]
) -> List[Product]:
    return [gen_random_product(categories, sellers) for _ in range(PRODUCTS_COUNT)]


def gen_and_dump_categories() -> List[str]:
    categories = [gen_random_string(24) for _ in range(CATEGORIES_COUNT)]
    with open(CATEGORIES_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(categories, f, indent=4)
    return categories


def gen_and_dump_sellers() -> List[uuid.UUID]:
    sellers = [str(uuid.uuid4()) for _ in range(SELLERS_COUNT)]
    with open(SELLERS_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(sellers, f, indent=4)
    return sellers


async def load_categories_in_pg(conn, categories: List[str]):
    query_str = "INSERT INTO plotva.product_categories (category_name) VALUES "
    for i in range(len(categories)):
        query_str += f"(${i + 1})"
        if i != len(categories) - 1:
            query_str += ", "
    query_str += ";"

    await conn.execute(query_str, *categories)


async def load_products_in_pg(conn, products_list: List[Product]):
    query_str = """
INSERT INTO
    plotva.products (product_id, name, description, seller_id, category, photo_url, price_rub, creation_time)
VALUES
    ($1, $2, $3, $4, $5, $6, $7, $8);
    """
    values = [
        (
            product.product_id,
            product.name,
            product.description,
            product.seller_id,
            product.category,
            product.photo_url,
            product.price_rub,
            product.creation_time,
        )
        for product in products_list
    ]

    await conn.executemany(query_str, values)


def init_paths():
    CATEGORIES_DATA_PATH.joinpath("./..").mkdir(parents=True, exist_ok=True)
    SELLERS_DATA_PATH.joinpath("./..").mkdir(parents=True, exist_ok=True)
    CATEGORIES_DATA_PATH.touch()
    SELLERS_DATA_PATH.touch()


async def main():
    init_paths()

    categories = gen_and_dump_categories()
    sellers = gen_and_dump_sellers()

    conn = await asyncpg.connect(
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        database=POSTGRES_DB,
        host=POSTGRES_HOST,
        port=int(POSTGRES_PORT),
    )

    await load_categories_in_pg(conn, categories)

    products = []
    for _ in range(PRODUCTS_COUNT):
        products.append(gen_random_product(categories, sellers))

    await load_products_in_pg(conn, products)

    await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
