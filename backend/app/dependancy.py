import datetime
from datetime import timedelta
import uuid
from fastapi import Depends, HTTPException, Header
from .models import Session, Token
from .config import TOKEN_TTL_SEC
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


async def get_session() -> AsyncSession:
    async with Session() as session:
        yield session

SessionDependency = Annotated[AsyncSession, Depends(get_session, use_cache=True)]

async def get_token(x_token: Annotated[uuid.UUID, Header()], session: SessionDependency) -> Token:
    query = select(Token).where(Token.token == x_token, 
    Token.creation_time >= (datetime.now() - timedelta(seconds=TOKEN_TTL_SEC)))
    result = await session.execute(query)
    token = result.scalars().unique().first()
    if token is None:
        raise HTTPException(401, 'Token not found')
    return token

TokenDependency = Annotated[Token, Depends(get_token)]

