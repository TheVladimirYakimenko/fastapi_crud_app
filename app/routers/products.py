from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.products import Product as ProductModel
from app.schemas import Product as ProductSchema, ProductCreate
from app.db_depends import get_async_db
from app.models.categories import Category as CategoryModel
from app.models.users import User as UserModel
from app.auth import get_current_seller


router = APIRouter(
    prefix='/products',
    tags=['products']
)


@router.get(
    path='/',
    status_code=status.HTTP_200_OK,
    response_model=list[ProductSchema]
)
async def get_all_products(db: AsyncSession = Depends(get_async_db)):
    '''
    Возвращает список всех товаров.
    '''
    stmt = select(ProductModel).where(
        ProductModel.is_active.is_(True)
    )
    result = await db.scalars(stmt)
    products = result.all()

    return products


@router.post(
    path='/',
    status_code=status.HTTP_201_CREATED,
    response_model=ProductSchema
)
async def create_product(
            product: ProductCreate,
            db: AsyncSession = Depends(get_async_db),
            user: UserModel = Depends(get_current_seller)
        ):
    '''
    Создает новый товар, привязанный к текущему продавцу (только для "seller")
    '''
    result = await db.scalars(
        select(CategoryModel.id).where(
            CategoryModel.id == product.category_id,
            CategoryModel.is_active.is_(True)
        )
    )
    category = result.first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Category not found or inactive'
        )

    new_product = ProductModel(seller_id=user.id, **product.model_dump())
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)

    return new_product


@router.get(
    path='/category/{category_id}',
    status_code=status.HTTP_200_OK,
    response_model=list[ProductSchema]
)
async def get_products_by_category(
            category_id: int,
            db: AsyncSession = Depends(get_async_db)
        ):
    '''
    Возвращает список товаров в указанной категории по ее ID
    '''
    stmt = select(CategoryModel).where(
        CategoryModel.id == category_id,
        CategoryModel.is_active.is_(True)
    )
    result = await db.scalars(stmt)
    category = result.first()

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Category not found'
        )

    stmt = select(ProductModel).where(
        ProductModel.category_id == category_id,
        ProductModel.is_active.is_(True)
    )
    result = await db.scalars(stmt)
    products = result.all()

    return products


@router.get(
    path='/{product_id}',
    status_code=status.HTTP_200_OK,
    response_model=ProductSchema
)
async def get_product(
            product_id: int,
            db: AsyncSession = Depends(get_async_db)
        ):
    '''
    Возвращает детальную информацию о товаре по его ID.
    '''
    stmt = select(ProductModel).where(
        ProductModel.id == product_id
    )
    result = await db.scalars(stmt)
    product = result.first()

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found'
        )

    return product


@router.put(
    path='/{product_id}',
    status_code=status.HTTP_200_OK,
    response_model=ProductSchema
)
async def update_product(
            product_id: int,
            product: ProductCreate,
            db: AsyncSession = Depends(get_async_db),
            current_user: UserModel = Depends(get_current_seller)
        ):
    '''
    Обновляет товар по его ID.
    '''
    result = await db.scalars(
        select(ProductModel).where(
            ProductModel.id == product_id
        )
    )
    db_product = result.first()

    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found'
        )

    if db_product.seller_id != current_user.id or current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You can only update your own products'
        )

    result = await db.scalars(
        select(CategoryModel).where(
            CategoryModel.id == db_product.category_id
        )
    )
    category = result.first()

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Category not found'
        )

    await db.execute(
        update(ProductModel).where(
            ProductModel.id == product_id
        ).values(
            **product.model_dump()
        )
    )
    await db.commit()
    await db.refresh(db_product)

    return db_product


@router.delete(
    path='/{product_id}',
    status_code=status.HTTP_200_OK
)
async def delete_product(
            product_id: int,
            db: AsyncSession = Depends(get_async_db),
            current_user: UserModel = Depends(get_current_seller)
        ):
    '''
    Удаляет товар по его ID.
    '''
    result = await db.scalars(
        select(ProductModel).where(
            ProductModel.id == product_id,
            ProductModel.is_active.is_(True)
        )
    )
    product = result.first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found'
        )

    if product.seller_id != current_user.id or current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You can only delete your own products'
        )

    product.is_active = False
    await db.commit()

    return {'status': 'success', 'message': 'Product deleted'}
