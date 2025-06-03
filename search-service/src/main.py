from fastapi import FastAPI
from fastapi import Response
from fastapi.responses import JSONResponse
from fastapi import status

from service import process

from logger import logger

from aiohttp import ClientError

app = FastAPI()

@app.get("/products")
async def search_products_by_name(name: str = None):
    try:
        if name:
            response_body = await process("products", {"name": name})
        else:
            response_body = await process("products")
        if response_body:
            logger.info("Search in index products done")
            return JSONResponse(response_body, status.HTTP_200_OK)
        else:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
    except ClientError as e:
        logger.error("Search in index products done with error")
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.get("/products")
async def search_products_by_category(category: str = None):
    try:
        if category:
            response_body = await process("products", {"category": category})
        else:
            response_body = await process("products")
        if response_body:
            logger.info("Search in index products done")
            return JSONResponse(response_body, status.HTTP_200_OK)
        else:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
    except ClientError as e:
        logger.error("Search in index products done with error")
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.get("/sellers")
async def search_sellers(name: str = None):
    try:
        if name:
            response_body = await process("sellers", {"name": name})
        else:
            response_body = await process("sellers")
        if response_body:
            logger.info("Search in index sellers done")
            return JSONResponse(response_body, status.HTTP_200_OK)
        else:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
    except ClientError as e:
        logger.error("Search in index sellers done with error")
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.get("/comments")
async def search_comments(content: str = None):
    try:
        if content:
            response_body = await process("comments", {"content": content})
        else:
            response_body = await process("comments")
        if response_body:
            logger.info("Search in index comments done")
            return JSONResponse(response_body, status.HTTP_200_OK)
        else:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
    except ClientError as e:
        logger.error("Search in index comments done with error")
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)