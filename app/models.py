import uuid
from typing import List

from pydantic import BaseModel, Field


class VectorEntity(BaseModel):
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    vector: List[float]
    label: str
