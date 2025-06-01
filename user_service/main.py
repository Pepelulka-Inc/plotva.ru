import os
import asyncio
import json
import logging
from uuid import UUID

from aiohttp import web
from dotenv import load_dotenv


from src.plotva.plugins.s3 import plugin_init, CephStorageProvider, CephStorage
from user_service.app.dtos.user_dtos import UpdateUserDTO, CreateUserDTO
from user_service.app.dtos.cart_dtos import (
    AddProductToCartDTO,
    ClearCartDTO,
    RemoveProductFromCartDTO,
)
from user_service.app.use_cases.user.update_user import UpdateUserUseCase
from user_service.app.use_cases.user.create_user import CreateUserUseCase
from user_service.app.use_cases.user.delete_user_by_id import DeleteUserByIdUseCase
from user_service.app.use_cases.user.get_all_users import GetAllUsersUseCase
from user_service.app.use_cases.user.get_by_email import GetUserByEmailUseCase
from user_service.app.use_cases.user.get_by_id import GetUserByIdUseCase
from user_service.app.use_cases.cart.add_to_cart import AddProductToCartUseCase
from user_service.app.use_cases.cart.delete_all_products import ClearCartUseCase
from user_service.app.use_cases.cart.delete_poduct import RemoveProductFromCartUseCase
from user_service.app.use_cases.cart.get_user_cart import GetUserCartByIdUseCase
from user_service.infrastructure.database.uow import UnitOfWork
from user_service.infrastructure.database.engine import init_db_and_tables, engine

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("user-service")


S3_ENDPOINT = os.getenv("S3_ENDPOINT")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_BUCKET = os.getenv("S3_BUCKET")

s3_client = plugin_init(
    endpoint_url=S3_ENDPOINT, access_key=S3_ACCESS_KEY, secret_key=S3_SECRET_KEY
).__next__()

s3_storage = CephStorageProvider(s3_client, S3_BUCKET).get_storage()


def get_s3_storage() -> CephStorage:
    return s3_storage


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)


async def get_uow(app: web.Application) -> UnitOfWork:
    return UnitOfWork(engine=app["engine"])


async def update_user_handler(request: web.Request) -> web.Response:
    try:
        user_id = UUID(request.match_info["user_id"])
        data = await request.json()
        dto = UpdateUserDTO(**data)

        uow = await get_uow(request.app)
        use_case = UpdateUserUseCase(uow=uow)

        updated_user = await use_case(user_id, dto)

        if not updated_user:
            return web.json_response({"error": "User not found"}, status=404)
        logger.info(f"User with email: {updated_user.email} updated")
        return web.json_response(updated_user.to_dict(), status=200)

    except Exception as e:
        logger.error(f"Error updating user: {e}", exc_info=True)
        return web.json_response({"error": "Internal server error"}, status=500)


async def create_user_handler(request: web.Request) -> web.Response:
    try:
        data = await request.json()
        dto = CreateUserDTO(**data)

        uow = await get_uow(request.app)
        use_case = CreateUserUseCase(uow=uow, s3_storage=app["s3_storage"])

        created_user = await use_case(dto)
        logger.info(f"User with email: {dto.email} created")
        return web.json_response(created_user.to_dict(), status=201)

    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return web.json_response({"error": "Internal server error"}, status=500)


async def delete_user_handler(request: web.Request) -> web.Response:
    try:
        user_id = UUID(request.match_info["user_id"])
        uow = await get_uow(request.app)
        use_case = DeleteUserByIdUseCase(uow=uow)

        deleted_user = await use_case(user_id)

        if not deleted_user:
            return web.json_response({"error": "User not found"}, status=404)
        logger.info(f"User with email: {deleted_user.email} удален")
        return web.json_response(deleted_user.to_dict(), status=200)

    except Exception as e:
        logger.error(f"Error deleting user: {e}", exc_info=True)
        return web.json_response({"error": "Internal server error"}, status=500)


async def get_all_users_handler(request: web.Request) -> web.Response:
    try:
        uow = await get_uow(request.app)
        use_case = GetAllUsersUseCase(uow=uow)

        users = await use_case()

        if not users:
            return web.json_response({"message": "No users found"}, status=200)

        logger.info("Cписок пользователей получен")
        return web.json_response([user.to_dict() for user in users], status=200)

    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        return web.json_response({"error": "Internal server error"}, status=500)


async def get_user_by_email_handler(request: web.Request) -> web.Response:
    try:
        user_email = request.query.get("email")
        if not user_email:
            return web.json_response({"error": "Email is required"}, status=400)

        uow = await get_uow(request.app)
        use_case = GetUserByEmailUseCase(uow=uow)

        user = await use_case(user_email)

        if not user:
            return web.json_response({"error": "User not found"}, status=404)
        logger.info(f"Запрошен пользователь {user_email}")
        return web.json_response(user.to_dict(), status=200)

    except Exception as e:
        logger.error(f"Error fetching user by email: {e}")
        return web.json_response({"error": "Internal server error"}, status=500)


async def get_user_by_id_handler(request: web.Request) -> web.Response:
    try:
        user_id = request.query.get("user_id")
        if not user_id:
            return web.json_response({"error": "Id is required"}, status=400)

        uow = await get_uow(request.app)
        use_case = GetUserByIdUseCase(uow=uow)

        user = await use_case(user_id)

        if not user:
            return web.json_response({"error": "User not found"}, status=404)
        logger.info(f"Запрошен пользователь {user_id}")
        return web.json_response(user.to_dict(), status=200)

    except Exception as e:
        logger.error(f"Error fetching user by email: {e}")
        return web.json_response({"error": "Internal server error"}, status=500)


async def get_user_cart_handler(request: web.Request) -> web.Response:
    try:
        user_id = UUID(request.match_info["user_id"])

        uow = await get_uow(request.app)
        use_case = GetUserCartByIdUseCase(uow=uow)

        cart_items = await use_case(user_id)

        if not cart_items:
            return web.json_response({"message": "Cart is empty"}, status=200)

        return web.json_response(
            [item.to_dict() for item in cart_items],
            status=200,
            dumps=lambda x: json.dumps(x, cls=UUIDEncoder),
        )

    except ValueError as ve:
        logger.warning(f"Validation error: {ve}")
        return web.json_response(
            {"error": "Invalid user_id format", "details": str(ve)}, status=400
        )

    except Exception as e:
        logger.error(f"Error fetching cart: {e}")
        return web.json_response({"error": "Internal server error"}, status=500)


async def add_product_to_cart_handler(request: web.Request) -> web.Response:
    try:
        data = await request.json()
        dto = AddProductToCartDTO(**data)

        uow = await get_uow(request.app)
        use_case = AddProductToCartUseCase(uow=uow)

        await use_case(dto)
        logger.info(f"Product {dto.product_id} add to users {dto.user_id} cart")
        return web.json_response({"status": "Product added to cart"}, status=201)

    except ValueError as ve:
        logger.warning(f"Validation error: {ve}")
        return web.json_response(
            {"error": "Invalid request data", "details": str(ve)}, status=400
        )

    except Exception as e:
        logger.error(f"Error adding product to cart: {e}", exc_info=True)
        return web.json_response({"error": "Internal server error"}, status=500)


async def clear_user_cart_handler(request: web.Request) -> web.Response:
    try:
        data = await request.json()
        dto = ClearCartDTO(**data)

        uow = await get_uow(request.app)
        use_case = ClearCartUseCase(uow=uow)

        result = await use_case(dto)

        if not result:
            return web.json_response(
                {"error": "Cart is already empty or user not found"}, status=404
            )
        logger.info(f"User {dto.user_id} cart cleared")
        return web.json_response({"status": "Cart cleared"}, status=200)

    except ValueError as ve:
        logger.warning(f"Validation error: {ve}")
        return web.json_response(
            {"error": "Invalid request data", "details": str(ve)}, status=400
        )

    except Exception as e:
        logger.error(f"Error clearing cart: {e}", exc_info=True)
        return web.json_response({"error": "Internal server error"}, status=500)


async def delete_from_cart_by_id_handler(request: web.Request) -> web.Response:
    try:
        data = await request.json()
        dto = RemoveProductFromCartDTO(**data)

        uow = await get_uow(request.app)
        use_case = RemoveProductFromCartUseCase(uow=uow)

        success = await use_case(dto)

        if not success:
            return web.json_response({"error": "Product not found in cart"}, status=404)
        logger.info(f"Пользователь {dto.user_id} удалил {dto.product_id} из корзины")
        return web.json_response({"status": "Product removed from cart"}, status=200)

    except ValueError as ve:
        logger.warning(f"Validation error: {ve}")
        return web.json_response(
            {"error": "Invalid request data", "details": str(ve)}, status=400
        )

    except Exception as e:
        logger.error(f"Error deleting product from cart: {e}")
        return web.json_response({"error": "Internal server error"}, status=500)


async def on_startup(app):
    try:
        await init_db_and_tables()
        logger.info("База данных инициализирована")
    except Exception as e:
        logger.error(f"Ошибка инициализации БД: {e}")
        raise


app = web.Application()
app["engine"] = engine
app["s3_storage"] = s3_storage

app.router.add_put("/users/{user_id}", update_user_handler)
app.router.add_post("/users", create_user_handler)
app.router.add_delete("/users/{user_id}", delete_user_handler)
app.router.add_get("/users/list", get_all_users_handler)
app.router.add_get("/users/email", get_user_by_email_handler)
app.router.add_get("/users/id", get_user_by_id_handler)

app.router.add_get("/cart/{user_id}", get_user_cart_handler)
app.router.add_post("/cart/add", add_product_to_cart_handler)
app.router.add_delete("/cart/clear", clear_user_cart_handler)
app.router.add_delete("/cart/remove", delete_from_cart_by_id_handler)


app.on_startup.append(on_startup)

if __name__ == "__main__":
    loop = asyncio.SelectorEventLoop()
    asyncio.set_event_loop(loop)
    web.run_app(app, port=9002)
