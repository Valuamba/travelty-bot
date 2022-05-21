from enum import Enum

from sqlalchemy import Column, Integer, String, func, DateTime, ARRAY, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

from app.models.sql.enums import ServiceType, PaymentType, TripStatus, JuridicalStatus
from app.models.sql.timebase import TimeBaseModelMixin, Base
from app.models.sql.types import IntEnum


class DriverProfile(TimeBaseModelMixin):
    user_id = Column('user_id', Integer, unique=False, nullable=False)
    contact_name = Column('contact_name', String, unique=False, nullable=False)
    company_name = Column('company_name', String, unique=False, nullable=True)
    about = Column('about', String, unique=False, nullable=True)
    phone_number = Column('phone_number', String(20), unique=False, nullable=True)
    caption_path = Column('caption_path', String, unique=True, nullable=True)
    juridical_status = Column('juridical_status', IntEnum(JuridicalStatus), unique=False, nullable=False)
    trip_status = Column('trip_status', IntEnum(TripStatus), unique=False, nullable=False)
    payment_type = Column('payment_type', IntEnum(PaymentType), unique=False, nullable=False)
    services = Column('services', ARRAY(IntEnum(ServiceType)), unique=False, nullable=False)
