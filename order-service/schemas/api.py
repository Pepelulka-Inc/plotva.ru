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

class UpdateStatusResponse(BaseResponse):
    status: Optional[str] = None
    updated_order_id: Optional[UUID] = None



    