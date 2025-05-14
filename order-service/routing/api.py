import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db_session
from sqlalchemy import exists, select, update
from schemas import api
from schemas import repositories
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError, NoResultFound, IntegrityError
from logging import getLogger

logger = getLogger()

api_router = APIRouter(prefix="/api", tags=["order_service_api"])

@api_router.post('/user/{user_id}/order/create')
async def create_order(
    user_id: uuid.UUID,
    data: api.CreateOrderRequest,
    session: AsyncSession = Depends(get_db_session)
):
    async with session.begin():
        if not await repositories.UsersModel.check_user(user_id, session):
            return api.CreateOrderResponse(error_message='Пользователь не найден')
        
        try:
            order = await repositories.OrdersModel.create_order(
                user_id=user_id,
                product_id_list=data.product_ids_list,
                amounts=data.amounts,
                order_time=data.order_time,
                shipped_time=data.shipped_time,
                address_id=data.address_id,
                session=session
            )
            return api.CreateOrderResponse(order_id=order.order_id)
        except ValueError as e:
            await session.rollback()
            raise HTTPException(status_code=400, detail=str(e))

@api_router.get('/user/{user_id}/orders')
async def get_user_orders(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session)
):
    try:
        orders = await session.execute(
            select(repositories.OrdersModel)
            .where(repositories.OrdersModel.user_id == user_id)
            .order_by(repositories.OrdersModel.order_date.desc())
        )
        orders_list = [order.to_dict() for order in orders.scalars().all()]
        
        return api.OrderResponse(
            order_data=orders_list
        )
        
    except SQLAlchemyError as e:
        return api.OrderResponse(
            error_message=f"Database error: {str(e)}"
        )
    except Exception as e:
        return api.OrderResponse(
            error_message=f"Unexpected error: {str(e)}"
        )

@api_router.get('/orders/{order_id}')
async def get_order_details(
    order_id: uuid.UUID, 
    session: AsyncSession = Depends(get_db_session)
):
    try:
        order = await session.execute(
            select(repositories.OrdersModel)
            .options(selectinload(repositories.OrdersModel.entries))
            .where(repositories.OrdersModel.order_id == order_id)
        )
        order_obj = order.scalar_one_or_none()
        
        if not order_obj:
            return repositories.OrderResponse(
                error_message="Order not found"
            )
            
        order_data = order_obj.to_dict()
        order_data['entries'] = [entry.to_dict() for entry in order_obj.entries]
        
        return api.OrderResponse(
            order_data=order_data
        )
        
    except SQLAlchemyError as e:
        return api.OrderResponse(
            error_message=f"Database error: {str(e)}"
        )
    except Exception as e:
        return api.OrderResponse(
            error_message=f"Unexpected error: {str(e)}"
        )

@api_router.post('/orders/{order_id}/status')
async def update_order_status(
    order_id: uuid.UUID,
    data: api.SetStatusRequest,
    session: AsyncSession = Depends(get_db_session)
):
    try:
        # Проверяем существование заказа
        order_exists = await session.execute(
            select(exists().where(repositories.OrdersModel.order_id == order_id))
        )
        if not order_exists.scalar():
            return api.sta(
                error_message=f"Заказ с ID {order_id} не найден",
                status=None,
                updated_order_id=None
            )

        # Обновляем статус
        await session.execute(
            update(repositories.OrdersModel)
            .where(repositories.OrdersModel.order_id == order_id)
            .values(status=data.new_status.value)
        )
        await session.commit()

        return api.UpdateStatusResponse(
            status="success",
            updated_order_id=order_id,
            error_message=None
        )

    except ValueError as e:
        await session.rollback()
        return api.UpdateStatusResponse(
            error_message=f"Некорректный статус: {str(e)}",
            status="error",
            updated_order_id=None
        )

    except NoResultFound:
        await session.rollback()
        return api.UpdateStatusResponse(
            error_message=f"Заказ с ID {order_id} не найден",
            status="error",
            updated_order_id=None
        )

    except IntegrityError as e:
        await session.rollback()
        logger.error(f"Integrity error updating order {order_id}: {str(e)}")
        return api.UpdateStatusResponse(
            error_message="Ошибка целостности данных",
            status="error",
            updated_order_id=None
        )

    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Database error updating order {order_id}: {str(e)}")
        return api.UpdateStatusResponse(
            error_message="Ошибка базы данных",
            status="error",
            updated_order_id=None
        )

    except Exception as e:
        await session.rollback()
        logger.error(f"Unexpected error updating order {order_id}: {str(e)}")
        return api.UpdateStatusResponse(
            error_message="Внутренняя ошибка сервера",
            status="error",
            updated_order_id=None
        )


