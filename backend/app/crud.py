from sqlalchemy.ext.asyncio import AsyncSession
from .models import ORM_OBJ, ORM_CLS
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

async def add_item(session: AsyncSession, item: ORM_OBJ):
    session.add(item)
    try:
        await session.commit()
        await session.refresh(item)
    except IntegrityError as err:
        print(f"IntegrityError: {err}")
        raise HTTPException(409, f'Item already exists: {str(err)}')

async def update_item(session: AsyncSession, item: ORM_OBJ):
    try:
        await session.commit()
    except IntegrityError as err:
        raise HTTPException(409, 'Update conflict')

async def get_item_by_id(session: AsyncSession, orm_cls: ORM_CLS, item_id: int) -> ORM_OBJ:
    query = select(orm_cls).where(orm_cls.id == item_id)
    result = await session.execute(query)
    orm_obj = result.scalars().unique().first()
    if orm_obj is None:
        raise HTTPException(404, 'Item not found')
    return orm_obj

async def delete_item(session: AsyncSession, item: ORM_OBJ):
    await session.delete(item)
    await session.commit()
