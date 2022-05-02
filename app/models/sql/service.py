from enum import Enum

from sqlalchemy import Column, Integer, String, func, DateTime, ARRAY
from sqlalchemy.orm import declarative_base, relationship

from app.models.sql.enums import ServiceType, PaymentType
from app.models.sql.timebase import TimeBaseModelMixin, Base
from app.models.sql.types import IntEnum


class Service(TimeBaseModelMixin):
    __tablename__ = "service"

    id = Column('id', Integer, primary_key=True)
    username = Column('username', String, unique=False)
    create_date = Column(DateTime, server_default=func.now())
    departure_date = Column('departure_date', DateTime, unique=False, nullable=True)
    driver_name = Column('driver_name', String, unique=False, nullable=True)

    departure_service = relationship("location", back_populates="service")
    arrival_service = relationship("location", back_populates="service")

    payment_type = Column('payment_type', IntEnum(PaymentType))
    services = Column('services', ARRAY(IntEnum(ServiceType)))

    # def __repr__(self):
    #     return f"{self.username}"
