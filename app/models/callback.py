from pydantic import Field

from app.models.base import TimeBaseModel


class CallbackModel(TimeBaseModel):
    user_id: int = Field(...)
    file_id: str = Field(...)

    class Collection:
        name = "CallbackModel"
