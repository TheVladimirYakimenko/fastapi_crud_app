from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User as UserModel
from app.config import Config, get_config
from app.db_depends import get_async_db


ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

config: Config = get_config()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='users/token')


def hash_password(password: str) -> str:
    """
    Преобразует пароль в хеш с использованием bcrypt.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, соответствует ли введённый пароль сохранённому хешу.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    '''
    Создает JWT с payload (sub, role, id, ext)
    '''
    to_encode = data.copy()
    expire = (datetime.now(timezone.utc)
              + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({'exp': expire})

    return jwt.encode(to_encode, config.secret_key, algorithm=config.algorithm)


def create_refresh_token(data: dict):
    '''
    Создает refresh-токен с длительным сроком действия.
    '''
    to_encode = data.copy()
    expire = (datetime.now(timezone.utc)
              + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, config.secret_key, algorithm=config.algorithm)


async def get_current_user(
            token: str = Depends(oauth2_scheme),
            db: AsyncSession = Depends(get_async_db)
        ):
    '''
    Проверяет JWT и возвращает пользователя из базы.
    '''
    try:
        payload = jwt.decode(
            token,
            config.secret_key,
            algorithms=[config.algorithm]
        )
        email: str = payload.get('sub')

        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Could not validate credentials',
                headers={'WWW-Authenticate': 'Bearer'}
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token has expired',
            headers={'WWW-Authenticate': 'Bearer'}
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
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_seller(
            current_seller: UserModel = Depends(get_current_user)
        ):
    '''
    Проверяет, что пользователь имеет роль "seller"
    '''
    if current_seller.role != 'seller':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Only sellers can perform this action'
        )
    return current_seller
