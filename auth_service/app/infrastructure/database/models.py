from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)


class User(DeclarativeBase):
    username: Mapped[str]
    email: Mapped[str]
    password: Mapped[str]
    