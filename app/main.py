from fastapi import FastAPI

from app.routers import categories, products, users, reviews
from app.config import Config, get_config


config: Config = get_config()
app = FastAPI(
    title='FastAPI интернет-магазин',
    version='0.1.0'
)

app.include_router(categories.router)
app.include_router(products.router)
app.include_router(users.router)
app.include_router(reviews.router)


@app.get('/')
async def root():
    '''
    Корневой маршрут, подтверждающий работоспособность FastAPI.
    '''
    return {'message': 'Добро пожаловать в FastAPI интернет-магазина!'}
