from sqlalchemy import Column, Integer, String, func, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from app.models.sql.timebase import TimeBaseModelMixin, Base


class Location(TimeBaseModelMixin):
    __tablename__ = "location"

    id = Column('id', Integer, primary_key=True)
    iso = Column('iso', String, unique=False, nullable=False)
    town = Column('town', String, unique=False, nullable=False)
    county = Column('county', String, unique=False, nullable=False)
    country = Column('country', String, unique=False, nullable=False)
    state = Column('state', String, unique=False, nullable=False)
    country_code = Column('country_code', String, unique=False, nullable=False)
    postcode = Column('postcode', Integer, unique=False, nullable=False)

    service_id = Column(Integer, ForeignKey('service.id'))
    service = relationship("User", back_populates="addresses")