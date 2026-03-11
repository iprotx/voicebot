from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db_session
from backend.storage.repositories import MessageRepository, UserRepository


async def get_user_repo(session: AsyncSession = Depends(get_db_session)) -> AsyncGenerator[UserRepository, None]:
    yield UserRepository(session)


async def get_message_repo(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[MessageRepository, None]:
    yield MessageRepository(session)
