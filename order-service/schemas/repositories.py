from datetime import datetime
from typing import List
from sqlalchemy import ForeignKey, Integer, BigInteger, select, text
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload
from schemas import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID, uuid4
from models import OrderStatus

class ProductCategoriesModel(BaseModel):
    __tablename__ = 'product_categories'
    
    category_name: Mapped[str] = mapped_column(primary_key=True, index=True)
    products: Mapped[List["ProductsModel"]] = relationship(
        "ProductsModel", backref="category_ref"
    )

class ProductsModel(BaseModel):
    __tablename__ = 'products'

    product_id: Mapped[UUID] = mapped_column(
        primary_key=True, index=True
    )
    name: Mapped[str] 
    description: Mapped[str]
    seller_id: Mapped[UUID] = mapped_column(
        ForeignKey("sellers.seller_id")
    )
    category: Mapped[str] = mapped_column(
        ForeignKey("product_categories.category_name")
    )
    photo_url: Mapped[str]
    creation_time: Mapped[datetime]
    price_rub: Mapped[int] = mapped_column(BigInteger)
    price_last_updated: Mapped[datetime]
    
    seller: Mapped["SellersModel"] = relationship(
        "SellersModel", backref="products"
    )
    comments: Mapped[List["CommentsModel"]] = relationship(
        "CommentsModel", backref="product"
    )
    shopping_cart_entries: Mapped[List["ShoppingCartEntriesModel"]] = relationship(
        "ShoppingCartEntriesModel", backref="product"
    )
    order_entries: Mapped[List["OrderEntriesModel"]] = relationship(
        "OrderEntriesModel", backref="product"
    )
    price_history: Mapped[List["ProductPricesHistoryModel"]] = relationship(
        "ProductPricesHistoryModel", backref="product"
    )

    async def get_product_name_by_id(
            self,
            session: AsyncSession,
            product_id: str
    ):
        name = await session.execute(select(ProductsModel.name).filter(
            product_id=ProductsModel.product_id
        ))
        result = name.scalars().all()
        return result
        

class CommentsModel(BaseModel):
    __tablename__ = 'comments'
    
    comment_id: Mapped[int] = mapped_column(
        primary_key=True, index=True
    )
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.product_id"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.user_id"))
    content: Mapped[str]
    rating: Mapped[int]
    time: Mapped[datetime]
    
    user_ref: Mapped["UsersModel"] = relationship(
        "UsersModel", backref="comments"
    )

class SellersModel(BaseModel):
    __tablename__ = 'sellers'
    
    seller_id: Mapped[UUID] = mapped_column(
        primary_key=True, index=True
    )
    name: Mapped[str]
    description: Mapped[str]
    photo_url: Mapped[str]
    phone_number: Mapped[str]
    email: Mapped[str]

class UsersModel(BaseModel):
    __tablename__ = 'users'
    
    user_id: Mapped[UUID] = mapped_column(
        primary_key=True, index=True
    )
    name: Mapped[str]
    surname: Mapped[str]
    photo_url: Mapped[str]
    phone_number: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] 
    hashed_password_base64: Mapped[str]
    
    addresses: Mapped[List["UserAddressesModel"]] = relationship(
        "UserAddressesModel", backref="user"
    )
    shopping_cart_entries: Mapped[List["ShoppingCartEntriesModel"]] = relationship(
        "ShoppingCartEntriesModel", backref="user"
    )
    orders: Mapped[List["OrdersModel"]] = relationship(
        "OrdersModel", backref="user"
    )

    @classmethod
    async def check_user(
            cls,
            user_id: UUID,
            session: AsyncSession
    ):
        result = await session.execute(select(
            UsersModel
        ).filter(
            UsersModel.user_id == user_id
        )
        )
        if result.scalar_one_or_none():
            return True
        else:
            return False
        

class UserAddressesModel(BaseModel):
    __tablename__ = 'user_addresses'
    
    address_id: Mapped[UUID] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.user_id"))
    country: Mapped[str]
    settlement: Mapped[str]
    street: Mapped[str]
    house_number: Mapped[str]
    apartment_number: Mapped[str]
    extra_info: Mapped[str] = mapped_column(nullable=True)
    
    orders: Mapped[List["OrdersModel"]] = relationship(
        "OrdersModel", backref="address"
    )

class ShoppingCartEntriesModel(BaseModel):
    __tablename__ = 'shopping_cart_entries'
    
    entry_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_id: Mapped[UUID] = mapped_column(
        ForeignKey("products.product_id"), index=True
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.user_id"), index=True
    )
    quantity: Mapped[int] = mapped_column(Integer)

class OrdersModel(BaseModel):
    __tablename__ = 'orders'
    
    order_id: Mapped[UUID] = mapped_column(
        primary_key=True, 
        default=uuid4,  # Добавляем генератор UUID по умолчанию
        server_default=text("gen_random_uuid()")  # И серверную генерацию
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.user_id")
    )
    address_id: Mapped[UUID] = mapped_column(
        ForeignKey("user_addresses.address_id")
    )
    status: Mapped[str]
    order_date: Mapped[datetime]
    shipped_date: Mapped[datetime]
    total_cost_rub: Mapped[int]
    
    entries: Mapped[List["OrderEntriesModel"]] = relationship(
        "OrderEntriesModel", backref="order"
    )

    @classmethod
    async def create_order(
        cls,
        user_id: UUID,
        product_id_list: List[UUID],
        amounts: List[int],
        order_time: datetime,
        shipped_time: datetime,
        address_id: UUID,
        session: AsyncSession
    ):
        if len(product_id_list) != len(amounts):
            raise ValueError("Количество товаров и количеств не совпадает")

        products = await session.execute(
            select(ProductsModel)
            .options(selectinload(ProductsModel.seller))
            .where(ProductsModel.product_id.in_(product_id_list))
            .order_by(ProductsModel.product_id)
        )
        products = products.scalars().all()

        if len(products) != len(product_id_list):
            found_ids = {str(p.product_id) for p in products}
            missing_ids = [str(pid) for pid in product_id_list if str(pid) not in found_ids]
            raise ValueError(f"Товары не найдены: {missing_ids}")

        total_cost = 0
        order_entries = []
        
        for i, product in enumerate(products):
            amount = amounts[i]
            total_cost += product.price_rub * amount
            
            order_entries.append(OrderEntriesModel(
                product_id=product.product_id,
                quantity=amount,
                product_name=product.name,
                product_price_rub=product.price_rub,
                product_seller_id=product.seller_id,
                product_seller_name=product.seller.name,
            ))

        order = OrdersModel(
            user_id=user_id,
            address_id=address_id,
            status=OrderStatus.PENDING.value,
            order_date=order_time,
            shipped_date=shipped_time,
            total_cost_rub=total_cost
        )
        
        session.add(order)
        await session.flush() 
        
        for entry in order_entries:
            entry.order_id = order.order_id
            session.add(entry)

        order.status = OrderStatus.SHIPPED.value
        return order
        

class OrderEntriesModel(BaseModel):
    __tablename__ = 'order_entries'
    
    entry_id: Mapped[int] = mapped_column(
        primary_key=True, index=True
    )
    order_id: Mapped[UUID] = mapped_column(ForeignKey("orders.order_id"))
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.product_id"))
    quantity: Mapped[int]
    product_name: Mapped[str]
    product_price_rub: Mapped[int]
    product_seller_id: Mapped[UUID]
    product_seller_name: Mapped[str]

class ProductPricesHistoryModel(BaseModel):
    __tablename__ = 'product_prices_history'
    
    entry_id: Mapped[int] = mapped_column(
        primary_key=True, index=True
    )
    product_id: Mapped[UUID] = mapped_column(
        ForeignKey("products.product_id"), index=True
    )
    price_rub: Mapped[int]
    valid_from: Mapped[datetime]
    valid_to: Mapped[datetime]