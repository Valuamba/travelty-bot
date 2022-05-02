import asyncio

from sqlalchemy import create_engine, ForeignKey, insert, DateTime, func
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.future import select
# alembic revision --autogenerate -m "Create user model"
# alembic upgrade heads

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


# engine = create_engine("postgresql://admin_db:16zomole@localhost:5432/travelty.test", echo=True, future=True)
# Base.metadata.create_all(bind=engine)

# stmt = (
#     insert(User).
#     values(username="Valentin")
# )
#
users = [
    User(username="Valentin")
]
#
# Session = sessionmaker(bind=engine)
# session = Session()


# def create_users():
#     for user in users:
#         session.add(user)
#     session.commit()

# create_users()

# user_records = session.query(User).all()
#
# for user in user_records:
#     print(f"USER: {user}")


async def async_main():
    addresses = [
        Address(email_address="some@mail.ru", user_id=8)
    ]

    engine = create_async_engine(
        "postgresql+asyncpg://admin_db:16zomole@localhost:5432/travelty.test", echo=True,
    )

    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)
    #     await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    async with async_session() as session:
        async with session.begin():
            # session.add_all(addresses)

         user_records = await session.execute(select(User))

        for user in user_records.scalars():
            print(f"USER: {user}")
        # await session.run_sync(fetch_and_update_objects)

        await session.commit()



    await engine.dispose()

asyncio.run(async_main())