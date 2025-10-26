from collections.abc import AsyncGenerator

from app.database import AsyncSession, async_session_maker


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    '''
    Зависимость для получения асинхронной сессии базы данных.
    Создает новую сессию для каждого запроса и закрывает ее после обработки.
    '''
    async with async_session_maker() as session:
        yield session
