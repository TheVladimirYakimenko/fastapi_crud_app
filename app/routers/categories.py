from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.categories import Category as CategoryModel
from app.schemas import Category as CategorySchema, CategoryCreate
from app.db_depends import get_async_db


router = APIRouter(
    prefix='/categories',
    tags=['categories'],
)


@router.get(
    path='/',
    response_model=list[CategorySchema],
    status_code=status.HTTP_200_OK
)
async def get_all_categories(db: AsyncSession = Depends(get_async_db)):
    '''
    Возвращает список всех категорий товаров.
    '''
    stmt = select(CategoryModel).where(
        CategoryModel.is_active.is_(True)
    )
    result = await db.scalars(stmt)
    categories = result.all()

    return categories


@router.post(
    '/',
    response_model=CategorySchema,
    status_code=status.HTTP_201_CREATED
)
async def create_category(
            category: CategoryCreate,
            db: AsyncSession = Depends(get_async_db)
        ):
    '''
    Создает новую категорию.
    '''
    if category.parent_id is not None:
        stmt = select(
            CategoryModel
            ).where(
                CategoryModel.id == category.parent_id,
                CategoryModel.is_active.is_(True)
                )
        result = await db.scalars(stmt)
        parent_id = result.first()

        if parent_id is None:
            raise HTTPException(
                status_code=400,
                detail='Parent category not found'
            )

    db_category = CategoryModel(**category.model_dump())
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)

    return db_category


@router.put(
    path='/{category_id}',
    response_model=CategorySchema,
)
async def update_category(
            category_id: int,
            category: CategoryCreate,
            db: AsyncSession = Depends(get_async_db)
        ):
    '''
    Обновляет категорию по ее ID.
    '''
    stmt = select(CategoryModel).where(
        CategoryModel.id == category_id,
        CategoryModel.is_active.is_(True)
    )
    result = await db.scalars(stmt)
    db_category = result.first()

    if db_category is None:
        raise HTTPException(
            status=404,
            detail='Category not found'
        )

    if category.parent_id is not None:
        stmt = select(CategoryModel).where(
            CategoryModel.id == category.parent_id,
            CategoryModel.is_active.is_(True)
        )
        result = await db.scalars(stmt)
        parent = result.first()

        if parent is None:
            raise HTTPException(
                status=404,
                detail='Parent category not found'
            )

    await db.execute(
        update(CategoryModel).where(
            CategoryModel.id == category_id
        ).values(
            **category.model_dump(exclude_unset=True)
        )
    )
    await db.commit()

    return db_category


@router.delete(
    path='/{category_id}',
    response_model=CategorySchema,
    status_code=status.HTTP_200_OK
)
async def delete_category(
            category_id: int,
            db: AsyncSession = Depends(get_async_db)
        ):
    '''
    Удаляет категорию по ее ID.
    '''
    stmt = select(CategoryModel).where(
        CategoryModel.id == category_id,
        CategoryModel.is_active.is_(True)
    )
    result = await db.scalars(stmt)
    category = result.first()

    if category is None:
        raise HTTPException(
            status_code=404,
            detail='Category not found'
        )

    category.is_active = False
    await db.commit()

    return category
