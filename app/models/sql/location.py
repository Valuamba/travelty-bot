from sqlalchemy import Column, Integer, String, func, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import declarative_base, relationship
from app.models.sql.timebase import TimeBaseModelMixin, Base


class Location(TimeBaseModelMixin):
    __tablename__ = "location"

    id = Column('id', Integer, primary_key=True)
    place_id = Column('place_id', BigInteger, unique=True, nullable=False)
    lat = Column('lat', String, unique=False, nullable=False)
    lon = Column('lon', String, unique=False, nullable=False)
    country = Column('country', String, unique=False, nullable=False)
    place = Column('place', String, unique=False, nullable=False)
    display_name = Column('display_name', String, unique=False, nullable=False)
