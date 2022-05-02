from abc import ABC

from sqlalchemy import Column, func, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class TimeBaseModelMixin(Base):
    __abstract__ = True

    updated_at = Column("updated_at", DateTime, server_default=func.now(), onupdate=func.current_timestamp())
    created_at = Column("created_at", DateTime, server_default=func.now())