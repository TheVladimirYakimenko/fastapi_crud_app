from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reviews import Review as ReviewModel
from app.models.users import User as UserModel
from app.models.products import Product as ProductModel
from app.schemas import ReviewCreate, Review as ReviewSchema
from app.db_depends import get_async_db
from app.auth import get_current_user


router = APIRouter(
    tags=['reviews']
)


async def update_product_rating(product_id: int, db: AsyncSession):
    result = await db.execute(
        select(func.avg(ReviewModel.grade)).where(
            ReviewModel.product_id == product_id,
            ReviewModel.is_active.is_(True)
        )
    )
    product_rating = result.scalar() or 0.0
    db.execute(
        update(ProductModel).where(
            ProductModel.id == product_id
        ).values(
            rating=product_rating
        )
    )
    await db.commit()


@router.get(
    path='/reviews',
    response_model=list[ReviewSchema],
    status_code=status.HTTP_200_OK
)
async def get_reviews(
            db: AsyncSession = Depends(get_async_db)
        ):
    result = await db.scalars(
        select(ReviewModel).where(
            ReviewModel.is_active.is_(True)
        )
    )
    reviews = result.all()

    return reviews


@router.get(
    path='/products/{product_id}/reviews',
    response_model=list[ReviewSchema],
    status_code=status.HTTP_200_OK
)
async def get_reviews_by_product(
            product_id: int,
            db: AsyncSession = Depends(get_async_db)
        ):
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
            detail='Product not found or inactive'
        )

    result = await db.scalars(
        select(ReviewModel).where(
            ReviewModel.product_id == product_id,
            ReviewModel.is_active.is_(True)
        )
    )
    reviews = result.all()

    return reviews


@router.post(
    path='/reviews',
    response_model=ReviewSchema,
    status_code=status.HTTP_201_CREATED
)
async def create_review(
            review: ReviewCreate,
            db: AsyncSession = Depends(get_async_db),
            user: UserModel = Depends(get_current_user)
        ):
    if user.role != 'buyer':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Only the buyer can make product reviews'
        )

    result = await db.scalars(
        select(ProductModel).where(
            ProductModel.id == review.product_id,
            ProductModel.is_active.is_(True)
        )
    )
    product = result.first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found or inactive'
        )

    new_review = ReviewModel(user_id=user.id, **review.model_dump())
    db.add(new_review)
    await db.commit()
    await update_product_rating(product_id=product.id, db=db)

    return new_review


@router.delete(
    path='/reviews/{review_id}'
)
async def delete_review(
            review_id: int,
            db: AsyncSession = Depends(get_async_db),
            user: UserModel = Depends(get_current_user)
        ):
    if user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Only the admin can delete product reviews'
        )

    result = await db.scalars(
        select(ReviewModel).where(
            ReviewModel.id == review_id,
            ReviewModel.is_active.is_(True)
        )
    )
    review = result.first()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Review not found or already deleted'
        )

    review.is_active = False
    await db.commit()
    await update_product_rating(product_id=review.product_id, db=db)

    return {'message': 'Review deleted'}
