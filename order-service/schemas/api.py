from typing import List, Optional, Union
from uuid import UUID
from pydantic import BaseModel as PydanticBaseModel, Field
from datetime import datetime, timedelta
from models import OrderStatus

class BaseRequest(PydanticBaseModel):
    user_id: str = Field(
        default='123e4567-e89b-12d3-a456-426655440000'
    )

class BaseResponse(PydanticBaseModel):
    error_message: Optional[str] = None

class CreateOrderRequest(BaseRequest):
    product_ids_list: List[str] = Field(
        default=["d9eebc99-9c0b-4ef8-bb6d-6bb9bd380a20","e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21"]
    )
    amounts: List[int] = Field(default=[1,2])
    order_time: datetime = Field(
        default=datetime.now()
    )
    shipped_time: datetime = Field(
        default=datetime.now()+timedelta(days=1)
    )
    address_id: str = Field(
        default="a6eebc99-9c0b-4ef8-bb6d-6bb9bd380a17"
    )

class CreateOrderResponse(BaseResponse):
    order_id: Optional[UUID] = None

class OrderResponse(BaseResponse):
    order_data: Optional[Union[dict, List[dict]]] = None

class SetStatusRequest(BaseRequest):
    order_id: UUID
    new_status: OrderStatus

class SetStatusResponse(BaseResponse):
    status: Optional[str] = None
    updated_order_id: Optional[UUID] = None

class DeleteOrderResponse(BaseResponse):
    order_id: UUID

class OrderEntryUpdate(PydanticBaseModel):
    entry_id: UUID = Field(..., description="ID позиции заказа")
    quantity: Optional[int] = Field(None, gt=0, description="Новое количество")
    remove: Optional[bool] = Field(False, description="Флаг удаления позиции")

class UpdateOrderRequest(BaseRequest):
    address_id: Optional[UUID] = Field(
        None, 
        description="Новый адрес доставки"
    )
    shipped_date: Optional[datetime] = Field(
        None,
        description="Новая дата доставки"
    )
    status: Optional[OrderStatus] = Field(
        None,
        description="Новый статус заказа"
    )
    entries: Optional[List[OrderEntryUpdate]] = Field(
        None,
        description="Список изменений позиций заказа"
    )
    note: Optional[str] = Field(
        None,
        max_length=500,
        description="Дополнительная заметка к заказу"
    )

class UpdatedOrderEntry(PydanticBaseModel):
    entry_id: UUID
    product_id: UUID
    product_name: str
    quantity: int
    price_rub: int
    status: str  # 'updated' | 'removed'

class UpdateOrderResponse(BaseResponse):
    updated_fields: List[str] = Field(
        [],
        description="Список обновленных полей"
    )
    new_status: Optional[OrderStatus] = Field(
        None,
        description="Актуальный статус заказа после обновления"
    )

    