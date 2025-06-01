from typing import List, Optional, Union
from uuid import UUID
from pydantic import BaseModel as PydanticBaseModel
from datetime import datetime
from models import OrderStatus


class BaseRequest(PydanticBaseModel):
    user_id: str


class BaseResponse(PydanticBaseModel):
    error_message: Optional[str] = None


class CreateOrderRequest(BaseRequest):
    product_ids_list: List[str]
    amounts: List[int]
    order_time: datetime
    shipped_time: datetime
    address_id: str


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
    entry_id: UUID
    quantity: Optional[int]
    remove: Optional[bool]


class UpdateOrderRequest(BaseRequest):
    address_id: Optional[UUID]
    shipped_date: Optional[datetime]
    status: Optional[OrderStatus]
    entries: Optional[List[OrderEntryUpdate]]
    note: Optional[str]


class UpdatedOrderEntry(PydanticBaseModel):
    entry_id: UUID
    product_id: UUID
    product_name: str
    quantity: int
    price_rub: int
    status: str  # 'updated' | 'removed'


class UpdateOrderResponse(BaseResponse):
    updated_fields: List[str]
    new_status: Optional[OrderStatus]
