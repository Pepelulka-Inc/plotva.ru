from datetime import datetime
from typing import List
from sqlalchemy import ForeignKey, Integer, BigInteger, delete, select, text
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID, uuid4
from order_service.models import OrderStatus
from sqlalchemy.ext.asyncio import AsyncAttrs, async_session
from sqlalchemy.orm import DeclarativeBase


class BaseModel(AsyncAttrs, DeclarativeBase):
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @classmethod
    async def insert(cls, session: async_session, *args, **kwargs):
        async with session.begin():
            session.add(cls(*args, **kwargs))
            await session.commit()

    @classmethod
    async def flush_insert(cls, session: async_session, *args, **kwargs):
        """
        метод вызывается только внутри уже открытой сессии
        async with session.begin():
        """
        cls_object = cls(**kwargs)
        session.add(cls_object)
        await session.flush()
        return cls_object


class ProductCategoriesModel(BaseModel):
    """Модель категорий товаров.

    Attributes:
        category_name: Название категории (первичный ключ)
        products: Список товаров в этой категории (отношение один-ко-многим)
    """

    __tablename__ = "product_categories"

    category_name: Mapped[str] = mapped_column(primary_key=True, index=True)
    products: Mapped[List["ProductsModel"]] = relationship(
        "ProductsModel", backref="category_ref"
    )


class ProductsModel(BaseModel):
    """Модель товаров в магазине.

    Attributes:
        product_id: UUID товара (первичный ключ)
        name: Название товара
        description: Описание товара
        seller_id: ID продавца (внешний ключ)
        category: Категория товара
        photo_url: URL изображения товара
        creation_time: Время создания записи
        price_rub: Цена в рублях
        price_last_updated: Время последнего обновления цены
    """

    __tablename__ = "products"
    __table_args__ = {"schema": "plotva"}

    product_id: Mapped[UUID] = mapped_column(primary_key=True, index=True)
    name: Mapped[str]
    description: Mapped[str]
    seller_id: Mapped[UUID] = mapped_column(ForeignKey("sellers.seller_id"))
    category: Mapped[str] = mapped_column(
        ForeignKey("product_categories.category_name")
    )
    photo_url: Mapped[str]
    creation_time: Mapped[datetime]
    price_rub: Mapped[int] = mapped_column(BigInteger)
    price_last_updated: Mapped[datetime]

    seller: Mapped["SellersModel"] = relationship("SellersModel", backref="products")
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

    async def get_product_name_by_id(self, session: AsyncSession, product_id: str):
        """
        Получает название товара по его ID.

        Args:
            session: Асинхронная сессия SQLAlchemy
            product_id: UUID товара для поиска

        Returns:
            Список названий товаров (обычно один элемент)
        """
        name = await session.execute(
            select(ProductsModel.name).filter(product_id=ProductsModel.product_id)
        )
        result = name.scalars().all()
        return result


class CommentsModel(BaseModel):
    __tablename__ = "comments"

    comment_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.product_id"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.user_id"))
    content: Mapped[str]
    rating: Mapped[int]
    time: Mapped[datetime]

    user_ref: Mapped["UsersModel"] = relationship("UsersModel", backref="comments")


class SellersModel(BaseModel):
    __tablename__ = "sellers"
    __table_args__ = {"schema": "plotva"}

    seller_id: Mapped[UUID] = mapped_column(primary_key=True, index=True)
    name: Mapped[str]
    description: Mapped[str]
    photo_url: Mapped[str]
    phone_number: Mapped[str]
    email: Mapped[str]


class UsersModel(BaseModel):
    __tablename__ = "users"
    __table_args__ = {"schema": "plotva"}

    user_id: Mapped[UUID] = mapped_column(primary_key=True, index=True)
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
    orders: Mapped[List["OrdersModel"]] = relationship("OrdersModel", backref="user")

    @classmethod
    async def check_user(cls, user_id: UUID, session: AsyncSession):
        result = await session.execute(
            select(UsersModel).filter(UsersModel.user_id == user_id)
        )
        if result.scalar_one_or_none():
            return True
        else:
            return False


class UserAddressesModel(BaseModel):
    __tablename__ = "user_addresses"
    __table_args__ = {"schema": "plotva"}
    address_id: Mapped[UUID] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.user_id"))
    country: Mapped[str]
    settlement: Mapped[str]
    street: Mapped[str]
    house_number: Mapped[str]
    apartment_number: Mapped[str]
    extra_info: Mapped[str] = mapped_column(nullable=True)

    orders: Mapped[List["OrdersModel"]] = relationship("OrdersModel", backref="address")


class ShoppingCartEntriesModel(BaseModel):
    __tablename__ = "shopping_cart_entries"
    __table_args__ = {"schema": "plotva"}
    entry_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_id: Mapped[UUID] = mapped_column(
        ForeignKey("products.product_id"), index=True
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.user_id"), index=True)
    quantity: Mapped[int] = mapped_column(Integer)


class OrdersModel(BaseModel):
    """Модель заказов в системе."""

    __tablename__ = "orders"
    __table_args__ = {"schema": "plotva"}
    order_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.user_id"))
    address_id: Mapped[UUID] = mapped_column(ForeignKey("user_addresses.address_id"))
    status: Mapped[str]
    order_date: Mapped[datetime]
    shipped_date: Mapped[datetime]
    total_cost_rub: Mapped[int]

    entries: Mapped[List["OrderEntriesModel"]] = relationship(
        "OrderEntriesModel", backref="order"
    )

    @classmethod
    async def get_user_orders(cls, session: AsyncSession, user_id: UUID):
        """
        Получает все заказы пользователя.

        Args:
            session: Асинхронная сессия SQLAlchemy
            user_id: UUID пользователя

        Returns:
            Список заказов в формате словарей
        """
        orders = await session.execute(
            select(OrdersModel)
            .where(OrdersModel.user_id == user_id)
            .order_by(OrdersModel.order_date.desc())
        )
        orders_list = [order.to_dict() for order in orders.scalars().all()]
        return orders_list

    @classmethod
    async def get_order(cls, session: AsyncSession, order_id: str):
        """
        Получает заказ по ID со всеми связанными позициями.

        Args:
            session: Асинхронная сессия SQLAlchemy
            order_id: UUID заказа

        Returns:
            Объект OrdersModel или None если не найден
        """
        order = await session.execute(
            select(OrdersModel)
            .options(selectinload(OrdersModel.entries))
            .where(OrdersModel.order_id == order_id)
        )
        order_obj = order.scalar_one_or_none()
        return order_obj

    async def update_status(self, session: AsyncSession, status: str):
        """
        Обновляет статус заказа с проверкой допустимых переходов.

        Args:
            session: Асинхронная сессия SQLAlchemy
            status: Новый статус заказа
        """

        new_status = OrderStatus(status)

        self.status = new_status.value

    @classmethod
    async def delete_order(cls, session: AsyncSession, order_id: UUID):
        """
        Удаляет заказ и все его позиции.

        Args:
            session: Асинхронная сессия SQLAlchemy
            order_id: UUID заказа для удаления
        """
        await session.execute(
            delete(OrderEntriesModel).where(OrderEntriesModel.order_id == order_id)
        )

        await session.execute(
            delete(OrdersModel).where(OrdersModel.order_id == order_id)
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
        session: AsyncSession,
    ):
        """
        Создает новый заказ с указанными товарами.

        Args:
            user_id: UUID пользователя
            product_id_list: Список ID товаров
            amounts: Количество каждого товара
            order_time: Время создания заказа
            shipped_time: Планируемое время доставки
            address_id: ID адреса доставки
            session: Асинхронная сессия SQLAlchemy

        Returns:
            Созданный объект OrdersModel

        Raises:
            ValueError: При несоответствии количества товаров и количеств
                       Если товары не найдены
        """
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
            missing_ids = [
                str(pid) for pid in product_id_list if str(pid) not in found_ids
            ]
            raise ValueError(f"Товары не найдены: {missing_ids}")

        total_cost = 0
        order_entries = []

        for i, product in enumerate(products):
            amount = amounts[i]
            total_cost += product.price_rub * amount

            order_entries.append(
                OrderEntriesModel(
                    product_id=product.product_id,
                    quantity=amount,
                    product_name=product.name,
                    product_price_rub=product.price_rub,
                    product_seller_id=product.seller_id,
                    product_seller_name=product.seller.name,
                )
            )

        order = OrdersModel(
            user_id=user_id,
            address_id=address_id,
            status=OrderStatus.PENDING.value,
            order_date=order_time,
            shipped_date=shipped_time,
            total_cost_rub=total_cost,
        )

        session.add(order)
        await session.flush()

        for entry in order_entries:
            entry.order_id = order.order_id
            session.add(entry)

        order.status = OrderStatus.SHIPPED.value
        return order

    @classmethod
    async def update_order(
        cls, session: AsyncSession, order_id: UUID, update_data: dict
    ):
        """
        Обновляет данные заказа.

        Args:
            session: Асинхронная сессия SQLAlchemy
            order_id: UUID заказа
            update_data: Словарь с полями для обновления

        Returns:
            Список обновленных полей

        Raises:
            ValueError: Если заказ не найден
        """
        order = await cls.get_order(session, order_id)

        if not order:
            raise ValueError("Order not found")

        updated_fields = []
        if "address_id" in update_data:
            order.address_id = update_data["address_id"]
            updated_fields.append("address_id")

        if "shipped_date" in update_data:
            order.shipped_date = update_data["shipped_date"]
            updated_fields.append("shipped_date")

        if "status" in update_data:
            await order.update_status(session, update_data["status"])
            updated_fields.append("status")

        if "entries" in update_data:
            total_cost = sum(
                entry.product_price_rub * entry.quantity for entry in order.entries
            )
            order.total_cost_rub = total_cost
            updated_fields.append("total_cost_rub")

        session.add(order)
        await session.commit()
        return updated_fields


class OrderEntriesModel(BaseModel):
    """Модель позиций заказа. Каждая запись представляет один товар в заказе"""

    __tablename__ = "order_entries"
    __table_args__ = {"schema": "plotva"}
    entry_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[UUID] = mapped_column(ForeignKey("orders.order_id"))
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.product_id"))
    quantity: Mapped[int]
    product_name: Mapped[str]
    product_price_rub: Mapped[int]
    product_seller_id: Mapped[UUID]
    product_seller_name: Mapped[str]


class ProductPricesHistoryModel(BaseModel):
    __tablename__ = "product_prices_history"
    __table_args__ = {"schema": "plotva"}
    entry_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_id: Mapped[UUID] = mapped_column(
        ForeignKey("products.product_id"), index=True
    )
    price_rub: Mapped[int]
    valid_from: Mapped[datetime]
    valid_to: Mapped[datetime]
