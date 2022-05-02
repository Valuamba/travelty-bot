from datetime import datetime
from enum import Enum, IntEnum
from typing import List
from pydantic import Field
from app.models.base import TimeBaseModel


class PaymentType(IntEnum):
    WithPayment = 1
    WithoutPayment = 2
    NotDecided = 3


class ServiceType(IntEnum):
    Passengers = 1
    PassengersWithPets = 2
    Documents = 3
    Package = 4


class ServiceModel(TimeBaseModel):
    id: int = Field(...)
    departure_date: datetime = Field(...)
    departure_town: str = Field(...)
    driver_name: str = Field(...)
    arrival_town: str = Field(...)
    payment_type: PaymentType = Field(...)
    service_types: List[ServiceType] = Field(...)

    class Collection:
        name = "RouteModel"



