from datetime import datetime, timezone
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from infrastructure.config.enums import TaskStatus


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)


class Task(Base):
    __tablename__ = "tasks"

    title: Mapped[str]
    description: Mapped[str]
    status: Mapped[str] = mapped_column(default=TaskStatus.TODO.value)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
    updated_at: Mapped[str] = mapped_column(nullable=True)
    user_id: Mapped[int]