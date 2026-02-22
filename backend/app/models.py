from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.sqlite import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


class Board(Base):
    """Kanban board model."""

    __tablename__ = "boards"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    columns: Mapped[list["Column"]] = relationship(
        "Column",
        back_populates="board",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    cards: Mapped[list["Card"]] = relationship(
        "Card",
        back_populates="board",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    labels: Mapped[list["Label"]] = relationship(
        "Label",
        back_populates="board",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class Column(Base):
    """Board column model."""

    __tablename__ = "columns"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    board_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("boards.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    position: Mapped[int] = mapped_column(nullable=False)
    color: Mapped[str] = mapped_column(String, default="#6B7280", nullable=False)

    # Relationships
    board: Mapped["Board"] = relationship("Board", back_populates="columns")
    cards: Mapped[list["Card"]] = relationship(
        "Card",
        back_populates="column",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class Card(Base):
    """Card/task model."""

    __tablename__ = "cards"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    board_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("boards.id", ondelete="CASCADE"), nullable=False
    )
    column_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("columns.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    position: Mapped[int] = mapped_column(nullable=False)
    priority: Mapped[str] = mapped_column(String, default="none", nullable=False)
    labels: Mapped[list] = mapped_column(JSON, default=[], nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    column: Mapped["Column"] = relationship("Column", back_populates="cards")
    board: Mapped["Board"] = relationship("Board", back_populates="cards")


class Label(Base):
    """Label/tag model."""

    __tablename__ = "labels"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    board_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("boards.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    color: Mapped[str] = mapped_column(String, nullable=False)

    # Relationships
    board: Mapped["Board"] = relationship("Board", back_populates="labels")
