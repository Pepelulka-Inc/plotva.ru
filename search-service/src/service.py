import aiohttp

from typing import List, Dict, Any


ES_URL = "http://elasticsearch:9200"

async def search(url: str, body: Dict[str, str] | None = None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, json=body) as response:
            if response.status != 200:
                if response.status != 404:
                    raise aiohttp.ClientError()
                else: 
                    return None
            else:
                return await response.json()
            

async def process(index: str, param: Dict[str, str] | None = None) -> List[str] | None:
    url = ES_URL + f"/{index}/_search"
    
    if param:
        query = {
            "query": {
                "match": {}
            }
        }
        for key, value in param.items():
            query["query"]["match"][key] = value
        response = await search(url, query)
    else:
        response = await search(url)
    if not response:
        return None
    hits = response['hits']['hits']
    if hits:
        res = []
        for doc in hits:
            res.append(doc["_id"])
        return res
    return None
    