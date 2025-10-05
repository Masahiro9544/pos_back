from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func
from db_control.connect import Base

class Products(Base):
    __tablename__ = "products"
    prd_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(50))
    price: Mapped[int] = mapped_column(Integer)

class Transaction(Base):
    __tablename__ = "transaction"
    trd_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    datetime: Mapped[str] = mapped_column(String(45))
    emp_cd: Mapped[str] = mapped_column(String(10))
    store_cd: Mapped[str] = mapped_column(String(5))
    pos_no: Mapped[str] = mapped_column(String(3))
    total_amt: Mapped[int] = mapped_column(Integer)
    ttl_amt_ex_tax: Mapped[int] = mapped_column(Integer)

class Details(Base):
    __tablename__ = "details"
    trd_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dtl_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prd_id: Mapped[int] = mapped_column(Integer)
    prd_code: Mapped[str] = mapped_column(String(13))
    prd_name: Mapped[str] = mapped_column(String(50))
    prd_price: Mapped[int] = mapped_column(Integer)