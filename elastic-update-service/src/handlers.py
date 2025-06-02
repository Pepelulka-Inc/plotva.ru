import aiohttp
import asyncio

import requests
from requests.exceptions import RequestException

from logger import logger

from typing import Dict, AnyStr, Any


ES_ENDPOINT = "http://elasticsearch:9200"

def init_indexes():
    try:
        requests.put(ES_ENDPOINT + "/products")
        logger.info("Products index created")
        requests.put(ES_ENDPOINT + "/sellers")
        logger.info("Sellers index created")
        requests.put(ES_ENDPOINT + "/comments")
        logger.info("Comments index created")
    except RequestException as e:
        logger.error("error creating indexes", exc_info=True)

async def do(data: Dict[AnyStr, Any]):
    print(data, flush=True)

# async def process_products_topic(data: Dict[AnyStr, Any]) -> None:
