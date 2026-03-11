from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db_session
from backend.services.security_service import JWT_ALG, JWT_SECRET
from backend.storage.repositories import AdminRepository, IntegrationRepository, MessageRepository, UserRepository

security = HTTPBearer()


async def get_user_repo(session: AsyncSession = Depends(get_db_session)) -> AsyncGenerator[UserRepository, None]:
    yield UserRepository(session)


async def get_message_repo(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[MessageRepository, None]:
    yield MessageRepository(session)


async def get_admin_repo(session: AsyncSession = Depends(get_db_session)) -> AsyncGenerator[AdminRepository, None]:
    yield AdminRepository(session)


async def get_integration_repo(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[IntegrationRepository, None]:
    yield IntegrationRepository(session)


def get_current_admin_email(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        email = payload.get("sub")
        if not email:
            raise ValueError("missing subject")
        return str(email)
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="invalid token")
