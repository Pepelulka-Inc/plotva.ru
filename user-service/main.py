import asyncio
import logging
from uuid import UUID
from aiohttp import web
from app.dtos.user_dtos import UpdateUserDTO, CreateUserDTO
from app.use_cases.user.update_user import UpdateUserUseCase
from app.use_cases.user.create_user import CreateUserUseCase
from infrastructure.database.uow import UnitOfWork
from infrastructure.database.engine import init_db_and_tables, engine


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("user-service")


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
        use_case = CreateUserUseCase(uow=uow)

        created_user = await use_case(dto)
        logger.info(f"User with email: {dto.email} created")
        return web.json_response(created_user.to_dict(), status=201)

    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return web.json_response({"error": "Internal server error"}, status=500)


app = web.Application()
app["engine"] = engine


async def on_startup(app):
    try:
        await init_db_and_tables()
        print("База данных инициализирована")
    except Exception as e:
        print(f"Ошибка инициализации БД: {e}")
        raise


app.router.add_put("/users/{user_id}", update_user_handler)
app.router.add_post("/users", create_user_handler)
app.on_startup.append(on_startup)

if __name__ == "__main__":
    loop = asyncio.SelectorEventLoop()
    asyncio.set_event_loop(loop)
    web.run_app(app, port=9002)
