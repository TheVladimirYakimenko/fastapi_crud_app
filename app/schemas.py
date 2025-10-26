from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict, EmailStr


class CategoryCreate(BaseModel):
    '''
    Модель для создания и обновления категории.
    Используется в POST и PUT запросах.
    '''
    name: str = Field(
        min_length=3,
        max_length=50,
        description='Название категории (3-50 символов)'
    )
    parent_id: int | None = Field(
        default=None,
        description='ID родительской категории, если есть'
    )


class Category(BaseModel):
    '''
    Модель для ответа с данными категории.
    Используется в GET-запросах.
    '''
    id: int = Field(
        description='Уникальный идентификатор категории'
    )
    name: str = Field(
        description='Название категории'
    )
    parent_id: int | None = Field(
        default=None,
        description='ID родительской категории, если есть'
    )
    is_active: bool = Field(
        description='Активность категории'
    )

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    name: str = Field(
        min_length=3,
        max_length=100,
        description='Название товара (от 3 до 100 символов)'
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description='Описание товара (до 500 символов)'
    )
    price: Decimal = Field(
        gt=0,
        description='Цена товара (больше 0)',
        decimal_places=2
    )
    image_url: str | None = Field(
        default=None,
        max_length=200,
        description='URL изображения товара'
    )
    stock: int = Field(
        ge=0,
        description='Количество товаров на складе (не менее 0)'
    )
    category_id: int = Field(
        description='ID категории, к которой относится товар'
    )


class Product(BaseModel):
    id: int = Field(
        description='Уникальный идентификатор товара'
    )
    name: str = Field(
        min_length=3,
        max_length=100,
        description='Название товара (от 3 до 100 символов)'
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description='Описание товара (до 500 символов)'
    )
    price: Decimal = Field(
        gt=0,
        description='Цена товара (больше 0)',
        decimal_places=2
    )
    image_url: str | None = Field(
        default=None,
        max_length=200,
        description='URL изображения товара'
    )
    stock: int = Field(
        ge=0,
        description='Количество товаров на складе (не менее 0)'
    )
    category_id: int = Field(
        description='ID категории, к которой относится товар'
    )
    is_active: bool = Field(
        description='Активность товара'
    )
    rating: float = Field(
        description='Рейтинг товара'
    )

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    email: EmailStr = Field(
        description='Email пользователя'
    )
    password: str = Field(
        min_length=8,
        description='Пароль (минимум 8 символов)'
    )
    role: str = Field(
        default='buyer',
        patter=r'^(buyer|seller|admin)$',
        description='Роль: "buyer", "seller" или "admin"'
    )


class User(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    role: str

    model_config = ConfigDict(from_attributes=True)


class ReviewCreate(BaseModel):
    product_id: int = Field(
        description='Уникальный идентификатор товара, к которому сделан отзыв'
    )
    comment: str = Field(
        description='Текстовое содержание отзыва',
        default=''
    )
    grade: int = Field(
        ge=1,
        le=5,
        description='Оценка к товару, к которому сделан отзыв'
    )


class Review(BaseModel):
    id: int = Field(
        description='Уникальный идентификатор отзыва'
    )
    user_id: int = Field(
        description='Уникальный идентификатор пользователя, сделавшего отзыв'
    )
    product_id: int = Field(
        description='Уникальный идентификатор товара, на который сделан отзыв'
    )
    comment: str = Field(
        description='Текстовое содержание отзыва'
    )
    comment_date: datetime = Field(
        description='Дата и время опубликования отзыва'
    )
    grade: int = Field(
        ge=1,
        le=5,
        description='Оценка к товару, к которому сделан отзыв'
    )
    is_active: bool = Field(
        description='Статус активности отзыва'
    )
