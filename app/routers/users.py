import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User as UserModel
from app.schemas import UserCreate, User as UserSchema
from app.db_depends import get_async_db
from app.auth import (
    hash_password, verify_password, create_access_token,
    create_refresh_token, get_config, Config
)


config: Config = get_config()
router = APIRouter(
    prefix='/users',
    tags=['users']
)


@router.post(
    path='/',
    response_model=UserSchema,
    status_code=status.HTTP_201_CREATED
)
async def create_user(
            user: UserCreate,
            db: AsyncSession = Depends(get_async_db)
        ):
    '''
    Регистрирует нового пользователя с ролью "buyer" или "seller"
    '''
    stmt = select(UserModel).where(
        UserModel.email == user.email
    )
    result = await db.scalars(stmt)

    if result.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Email already registered'
        )

    db_user = UserModel(
        email=user.email,
        hashed_password=hash_password(user.password),
        role=user.role
    )
    db.add(db_user)
    await db.commit()

    return db_user


@router.post(
    path='/token'
)
async def login(
            form_data: OAuth2PasswordRequestForm = Depends(),
            db: AsyncSession = Depends(get_async_db)
        ):
    result = await db.scalars(
        select(UserModel).where(
            UserModel.email == form_data.username,
            UserModel.is_active.is_(True)
        )
    )
    user = result.first()

    if (not user
            or not verify_password(form_data.password, user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect email or password',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    access_token = create_access_token(
        data={'sub': user.email, 'role': user.role, 'id': user.id}
    )
    refresh_token = create_refresh_token(
        data={'sub': user.email, 'role': user.role, 'id': user.id}
    )
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer'
    }


@router.post(
    path='/refresh-token'
)
async def refresh_token(
            refresh_token: str,
            db: AsyncSession = Depends(get_async_db),
        ):
    '''
    Обновляет access_token с помощью refresh_token.
    '''
    try:
        payload = jwt.decode(
            refresh_token,
            config.secret_key,
            algorithms=[config.algorithm]
        )
        email: str = payload.get('sub')

        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate refresh token",
                headers={"WWW-Authenticate": "Bearer"}
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    result = await db.scalars(
        select(UserModel).where(
            UserModel.email == email,
            UserModel.is_active.is_(True)
        )
    )
    user = result.first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(
        data={'sub': user.email, 'role': user.role, 'id': user.id}
    )
    return {'access_token': access_token, 'token_type': 'bearer'}
