from datetime import datetime

from sqlalchemy import Integer, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.database import Base


class Review(Base):
    __tablename__ = 'reviews'

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('users.id')
    )
    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('products.id')
    )
    comment: Mapped[str] = mapped_column(
        Text
    )
    comment_date: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now
    )
    grade: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    user: Mapped['User'] = relationship(
        'User',
        back_populates='reviews'
    )
    product: Mapped['Product'] = relationship(
        'Product',
        back_populates='reviews'
    )

    @validates('grade')
    def validate_age(self, key, grade):
        if 1 <= grade <= 5:
            return grade
        raise ValueError('Оценка должна находиться в диапазоне от 1 до 5')
