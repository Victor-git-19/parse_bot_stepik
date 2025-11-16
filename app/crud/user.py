from datetime import datetime as dt

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def create_user(
    session: AsyncSession,
    tg_id: int,
    name: str,
    stepik_url: str,
) -> User:

    result = await session.execute(select(User).where(User.tg_id == tg_id))
    user = result.scalar_one_or_none()

    if user:
        user.name = name
        user.stepik_url = stepik_url
        user.last_update = dt.utcnow()
    else:
        user = User(
            tg_id=tg_id,
            name=name,
            stepik_url=stepik_url,
            last_update=dt.utcnow(),
        )
        session.add(user)

    await session.commit()
    await session.refresh(user)
    return user


async def get_user_by_tg_id(
    session: AsyncSession,
    tg_id: int,
) -> User | None:
    result = await session.execute(select(User).where(User.tg_id == tg_id))
    return result.scalar_one_or_none()


async def update_user_progress(
    session: AsyncSession,
    tg_id: int,
    *,
    solved_tasks: int,
) -> User | None:
    result = await session.execute(select(User).where(User.tg_id == tg_id))
    user = result.scalar_one_or_none()

    if not user:
        return None

    user.solved_tasks = solved_tasks
    user.last_update = dt.utcnow()

    await session.commit()
    await session.refresh(user)
    return user
