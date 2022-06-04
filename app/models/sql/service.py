from enum import Enum

from sqlalchemy import Column, Integer, String, func, DateTime, ARRAY, ForeignKey, BigInteger
from sqlalchemy.orm import declarative_base, relationship

from app.models.sql.enums import ServiceType, PaymentType, TripStatus, JuridicalStatus
from app.models.sql.timebase import TimeBaseModelMixin, Base
from app.models.sql.types import IntEnum


class Trip(TimeBaseModelMixin):
    __tablename__ = "trip"

    id = Column('id', Integer, primary_key=True)
    user_id = Column('user_id', BigInteger, unique=False, nullable=False)
    contact_name = Column('contact_name', String, unique=False, nullable=True)
    company_name = Column('company_name', String, unique=False, nullable=True)
    commentary = Column('commentary', String, unique=False, nullable=True)
    departure_dates = Column('departure_date', ARRAY(String), unique=False, nullable=False)
    phone_number = Column('phone_number', String(20), unique=False, nullable=True)
    caption_path = Column('caption_path', String, unique=True, nullable=True)
    juridical_status = Column('juridical_status', IntEnum(JuridicalStatus), unique=False, nullable=False)
    trip_status = Column('trip_status', IntEnum(TripStatus), unique=False, nullable=False)
    payment_type = Column('payment_type', IntEnum(PaymentType), unique=False, nullable=False)
    services = Column('services', ARRAY(IntEnum(ServiceType)), unique=False, nullable=False)

    departure_location_id = Column(Integer, ForeignKey('location.id'))
    arrival_location_id = Column(Integer, ForeignKey('location.id'))
    address_1_id = Column(Integer, ForeignKey('location.id'), nullable=True)
    address_2_id = Column(Integer, ForeignKey('location.id'), nullable=True)
    address_3_id = Column(Integer, ForeignKey('location.id'), nullable=True)

    departure_location = relationship("Location", foreign_keys=[departure_location_id])
    arrival_location = relationship("Location", foreign_keys=[arrival_location_id])
    address_1 = relationship("Location", foreign_keys=[address_1_id])
    address_2 = relationship("Location", foreign_keys=[address_2_id])
    address_3 = relationship("Location", foreign_keys=[address_3_id])

    # def __repr__(self):
    #     return f"{self.username}"
