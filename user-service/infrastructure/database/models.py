from sqlalchemy import Column, Integer, String, Uuid, ForeignKey, BigInteger
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class UserModel(Base):
    __tablename__ = "users"
    user_id = Column(Uuid, primary_key=True)
    name = Column(String(255), nullable=False)
    surname = Column(String(255), nullable=False)
    photo_url = Column(String(255))
    phone_number = Column(String(20))
    email = Column(String(255), unique=True, nullable=False)
    hashed_password_base64 = Column(String(255), nullable=False)

    cart_entries = relationship("ShoppingCartEntry", back_populates="user")


class ShoppingCartEntry(Base):
    __tablename__ = "shopping_cart_entries"
    entry_id = Column(BigInteger, primary_key=True)
    product_id = Column(Uuid, nullable=False)
    user_id = Column(Uuid, ForeignKey("users.user_id"), nullable=False)
    quantity = Column(Integer, default=1)

    user = relationship("User", back_populates="cart_entries")
