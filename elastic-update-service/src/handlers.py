import aiohttp
import asyncio

import requests
from requests.exceptions import RequestException

from logger import logger

from typing import Dict, AnyStr, Any


ES_ENDPOINT = "http://elasticsearch:9200"

def init_indexes():
    config_products = {
        "settings": {
            "analysis": {
                "analyzer": {
                    "russian_english_analyzer": {
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "russian_stemmer",
                            "english_stemmer",
                        ],
                    }
                },
                "filter": {
                    "russian_stemmer": {"type": "stemmer", "language": "russian"},
                    "english_stemmer": {"type": "stemmer", "language": "english"},
                },
            }
        },
        "mappings": {
            "properties": {
                "name": {"type": "text", "analyzer": "russian_english_analyzer"},
                "id": {"type": "keyword", "index": False},
                "category": {"type": "text", "analyzer": "russian_english_analyzer"}
            }
        },
    }

    config_sellers = {
        "settings": {
            "analysis": {
                "analyzer": {
                    "russian_english_analyzer": {
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "russian_stemmer",
                            "english_stemmer",
                        ],
                    }
                },
                "filter": {
                    "russian_stemmer": {"type": "stemmer", "language": "russian"},
                    "english_stemmer": {"type": "stemmer", "language": "english"},
                },
            }
        },
        "mappings": {
            "properties": {
                "name": {"type": "text", "analyzer": "russian_english_analyzer"},
                "id": {"type": "keyword", "index": False}
            }
        },
    }

    config_comments = {
        "settings": {
            "analysis": {
                "analyzer": {
                    "russian_english_analyzer": {
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "russian_stemmer",
                            "english_stemmer",
                        ],
                    }
                },
                "filter": {
                    "russian_stemmer": {"type": "stemmer", "language": "russian"},
                    "english_stemmer": {"type": "stemmer", "language": "english"},
                },
            }
        },
        "mappings": {
            "properties": {
                "content": {"type": "text", "analyzer": "russian_english_analyzer"},
                "id": {"type": "keyword", "index": False}
            }
        },
    }
    try:
        requests.put(ES_ENDPOINT + "/products", config_products)
        logger.info("products index created")
        requests.put(ES_ENDPOINT + "/sellers", config_sellers)
        logger.info("sellers index created")
        requests.put(ES_ENDPOINT + "/comments", config_comments)
        logger.info("comments index created")
    except RequestException as e:
        logger.error("error creating indexes", exc_info=True)


async def add_to_es(url: str, data: dict, topic_name: str) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, json=data) as response:
            if response.status == 201:
                id = data["id"]
                logger.info(f"doc with id = {id} added in elastic in index {topic_name}")
            else:
                raise aiohttp.ClientError()
            
async def del_from_es(url: str, id: str, topic_name: str) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.delete(url=url) as response:
            if response.status == 200:
                logger.info(f"doc with id = {id} delete from elastic in index {topic_name}")
            else:
                raise aiohttp.ClientError()

async def process_topic(data: Dict[AnyStr, Any], topic_name: str) -> None:
    try:
        if data["action"] == "add":
            try:
                id = data["id"]
                name = data["name"]
                body = {
                    "name": name,
                    "id": id
                }
                if topic_name == "products":
                    body["category"] = data["category"]

                url = ES_ENDPOINT + f"/{topic_name}/_doc/{id}"
                
                await add_to_es(url, body, topic_name)
            except aiohttp.ClientError as e:
                logger.error(f"Can't add doc with id = {id} in elastic in index {topic_name}")
        elif data["action"] == "delete":
            try:
                id = data["id"]
                url = ES_ENDPOINT + f"/{topic_name}/_doc/{id}"
                await del_from_es(url, id, topic_name)
            except aiohttp.ClientError as e:
                logger.error(f"Can't delete product with id = {id} in elastic in index {topic_name}")
    except Exception as e:
        logger.error(f"wrong message from topic {topic_name}")
