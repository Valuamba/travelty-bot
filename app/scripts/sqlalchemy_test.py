import asyncio
import pprint

import sqlalchemy
from sqlalchemy import create_engine, ForeignKey, insert, DateTime, func, update
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, selectinload, joinedload
from sqlalchemy.future import select
# alembic revision --autogenerate -m "Create user model"
# alembic upgrade heads
from app.models.sql.enums import TripStatus
from app.models.sql.location import Location
from app.models.sql.service import Trip

metadata_obj = MetaData()
engine = create_engine("postgresql://admin_db:16zomole@localhost:5432/travelty.test", echo=True, future=True)

# user_table = Table(
#     "user_account",
#     metadata_obj,
#     Column('id', Integer, primary_key=True),
#     Column('name', String(30)),
#     Column('fullname', String)
# )

Base = declarative_base()


class User(Base):
    __tablename__ = "person"

    id = Column('id', Integer, primary_key=True)
    username = Column('username', String, unique=False)
    create_date = Column(DateTime, server_default=func.now())

    addresses = relationship("Address", back_populates="user")

    def __repr__(self):
        return f"{self.username}"


class Address(Base):
    __tablename__ = 'address'

    id = Column(Integer, primary_key = True)
    email_address = Column(String, nullable=False)
    create_date = Column(DateTime, server_default=func.now())

    user_id = Column(Integer, ForeignKey('person.id'))
    user = relationship("User", back_populates="addresses")


async def async_main():
    engine = create_async_engine(
        "postgresql+asyncpg://admin_db:16zomole@localhost:5432/travelty.test", echo=True,
    )

    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    async with async_session() as session:
        async with session.begin():
            stmt = (
                update(Trip)
                    .returning(Trip)
                    .where(Trip.id == 9)
                    .values(trip_status=TripStatus.Published)
            )

            s_query = select(Trip)\
                .from_statement(stmt) \
                .options(joinedload(Trip.arrival_location), selectinload(Trip.departure_location))

            result = await session.execute(s_query)
            s_res = result.scalar()

            dd = s_res.__dict__

            for r in s_res:
                for al in r.arrival_location:
                    print(al)
            pprint.pprint(s_res)

            result = await session.execute(orm_stmt)
            m = result.scalar()

            pprint.pprint(m)

    await engine.dispose()

asyncio.run(async_main())