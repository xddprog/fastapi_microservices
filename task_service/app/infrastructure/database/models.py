from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from task_service.app.infrastructure.config.enums import TaskStatus


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)


class Task(Base):
    __tablename__ = "tasks"

    title: Mapped[str]
    description: Mapped[str]
    status: Mapped[str] = mapped_column(default=TaskStatus.TODO)
    created_at: Mapped[str]
    updated_at: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))