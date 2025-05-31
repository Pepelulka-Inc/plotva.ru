import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db_session
from schemas import api
from schemas import repositories
from sqlalchemy.exc import SQLAlchemyError
import logging

print("zovzovzov")
logger = logging.getLogger(__name__)

api_router = APIRouter(prefix="/api", tags=["order_service_api"])


@api_router.post("/user/{user_id}/order/create")
async def create_order(
    user_id: uuid.UUID,
    data: api.CreateOrderRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Создает новый заказ для указанного пользователя.

    Args:
        user_id: UUID пользователя
        data: Данные для создания заказа (список товаров, количество и т.д.)
        session: Асинхронная сессия базы данных

    Returns:
        CreateOrderResponse с ID созданного заказа или сообщением об ошибке

    Raises:
        HTTPException 400: При ошибках валидации данных
        HTTPException 500: При внутренних ошибках сервера
    """
    logger.info(f"Creating order for user {user_id} with data: {data.model_dump()}")
    async with session.begin():
        try:
            logger.debug(f"Checking if user {user_id} exists")
            if not await repositories.UsersModel.check_user(user_id, session):
                logger.warning(f"User {user_id} not found")
                return api.CreateOrderResponse(error_message="Пользователь не найден")

            logger.debug(f"Creating order with products: {data.product_ids_list}")
            order = await repositories.OrdersModel.create_order(
                user_id=user_id,
                product_id_list=data.product_ids_list,
                amounts=data.amounts,
                order_time=data.order_time,
                shipped_time=data.shipped_time,
                address_id=data.address_id,
                session=session,
            )

            logger.info(f"Order created successfully: {order.order_id}")
            return api.CreateOrderResponse(order_id=order.order_id)

        except ValueError as e:
            logger.error(f"Validation error creating order: {str(e)}")
            await session.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.critical(f"Unexpected error creating order: {str(e)}", exc_info=True)
            await session.rollback()
            raise HTTPException(status_code=500, detail="Internal server error")


@api_router.get("/user/{user_id}/orders")
async def get_user_orders(
    user_id: uuid.UUID, session: AsyncSession = Depends(get_db_session)
):
    """
    Получает список всех заказов пользователя.

    Args:
        user_id: UUID пользователя
        session: Асинхронная сессия базы данных

    Returns:
        OrderResponse со списком заказов или сообщением об ошибке
    """
    logger.info(f"Fetching orders for user {user_id}")
    try:
        logger.debug("Executing get_user_orders query")
        orders = await repositories.OrdersModel.get_user_orders(session, user_id)

        logger.debug(f"Found {len(orders)} orders")
        return api.OrderResponse(order_data=orders)

    except SQLAlchemyError as e:
        logger.error(f"Database error fetching orders: {str(e)}", exc_info=True)
        return api.OrderResponse(error_message="Database error")
    except Exception as e:
        logger.critical(f"Unexpected error fetching orders: {str(e)}", exc_info=True)
        return api.OrderResponse(error_message="Internal server error")


@api_router.get("/orders/{order_id}")
async def get_order_details(
    order_id: uuid.UUID, session: AsyncSession = Depends(get_db_session)
):
    """
    Получает детальную информацию о конкретном заказе.

    Args:
        order_id: UUID заказа
        session: Асинхронная сессия базы данных

    Returns:
        OrderResponse с данными заказа или сообщением об ошибке
    """
    logger.info(f"Fetching details for order {order_id}")
    try:
        logger.debug("Executing get_order query")
        order_obj = await repositories.OrdersModel.get_order(
            session=session, order_id=order_id
        )

        if not order_obj:
            logger.warning(f"Order {order_id} not found")
            return api.OrderResponse(error_message="Order not found")

        logger.debug("Serializing order data")
        order_data = order_obj.to_dict()
        order_data["entries"] = [entry.to_dict() for entry in order_obj.entries]

        logger.info(f"Successfully retrieved order {order_id}")
        return api.OrderResponse(order_data=order_data)

    except SQLAlchemyError as e:
        logger.error(f"Database error fetching order: {str(e)}", exc_info=True)
        return api.OrderResponse(error_message="Database error")
    except Exception as e:
        logger.critical(f"Unexpected error fetching order: {str(e)}", exc_info=True)
        return api.OrderResponse(error_message="Internal server error")


@api_router.post("/orders/{order_id}/status")
async def update_order_status(
    order_id: uuid.UUID,
    data: api.SetStatusRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Обновляет статус заказа.

    Args:
        order_id: UUID заказа
        data: Новый статус заказа
        session: Асинхронная сессия базы данных

    Returns:
        SetStatusResponse с новым статусом или сообщением об ошибке
    """
    logger.info(f"Updating status for order {order_id} to {data.new_status}")
    async with session.begin():
        try:
            logger.debug(f"Fetching order {order_id}")
            order_obj = await repositories.OrdersModel.get_order(session, order_id)
            if not order_obj:
                logger.warning(f"Order {order_id} not found for status update")
                return api.SetStatusResponse(
                    error_message=f"Заказ с ID {order_id} не найден",
                    status=None,
                    updated_order_id=None,
                )

            logger.debug(
                f"Current status: {order_obj.status}, new status: {data.new_status}"
            )
            await order_obj.update_status(session, status=data.new_status)

            logger.info(f"Status updated successfully for order {order_id}")
            print(order_obj.status)
            await session.commit()
            return api.SetStatusResponse(
                status=data.new_status, updated_order_id=order_id, error_message=None
            )

        except SQLAlchemyError as e:
            logger.error(
                f"Database error updating order {order_id}: {str(e)}", exc_info=True
            )
            await session.rollback()
            return api.SetStatusResponse(
                error_message="Ошибка базы данных",
                status="error",
                updated_order_id=None,
            )

        except Exception as e:
            logger.critical(
                f"Unexpected error updating order {order_id}: {str(e)}", exc_info=True
            )
            await session.rollback()
            return api.SetStatusResponse(
                error_message="Внутренняя ошибка сервера",
                status="error",
                updated_order_id=None,
            )


@api_router.delete("/orders/{order_id}/delete")
async def delete_order(
    order_id: uuid.UUID, session: AsyncSession = Depends(get_db_session)
):
    """
    Удаляет заказ и все связанные с ним данные.

    Args:
        order_id: UUID заказа для удаления
        session: Асинхронная сессия базы данных

    Returns:
        DeleteOrderResponse с результатом операции

    Raises:
        HTTPException 404: Если заказ не найден
        HTTPException 500: При ошибках базы данных
    """
    logger.info(f"Deleting order {order_id}")
    async with session.begin():
        try:
            order_obj = await repositories.OrdersModel.get_order(session, order_id)
            if not order_obj:
                logger.warning(f"Order {order_id} not found for deletion")
                raise HTTPException(status_code=404, detail="Order not found")

            await order_obj.delete_order(session, order_id)
            await session.commit()
            logger.info(f"Order {order_id} deleted successfully")
            return api.DeleteOrderResponse(error_message="", order_id=order_id)

        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Database error deleting order: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
        except Exception as e:
            await session.rollback()
            logger.error(f"Unexpected error deleting order: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")


@api_router.patch("/orders/{order_id}/update")
async def update_order(
    order_id: uuid.UUID,
    data: api.UpdateOrderRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Частично обновляет данные заказа.

    Поддерживает обновление:
    - адреса доставки
    - даты доставки
    - статуса заказа

    Args:
        order_id: UUID заказа
        data: Данные для обновления
        session: Асинхронная сессия базы данных

    Returns:
        UpdateOrderResponse со списком измененных полей или ошибкой
    """
    logger.info(f"Updating order {order_id}")
    async with session.begin():
        try:
            update_data = data.model_dump(exclude_unset=True)

            updated_fields = await repositories.OrdersModel.update_order(
                session, order_id, update_data
            )

            return api.UpdateOrderResponse(
                updated_fields=updated_fields, error_message=None
            )

        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Database error: {str(e)}", exc_info=True)
            return api.UpdateOrderResponse(
                error_message="Database error", updated_fields=[], new_status=None
            )
        except Exception as e:
            await session.rollback()
            logger.critical(f"Unexpected error: {str(e)}", exc_info=True)
            return api.UpdateOrderResponse(
                error_message="Internal server error",
                updated_fields=[],
                new_status=None,
            )
