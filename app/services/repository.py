from sqlalchemy.ext.asyncio import AsyncSession


def get_users(session: AsyncSession):
    session