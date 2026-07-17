from pydantic import BaseModel
from typing import List, Optional

class DanceBase(BaseModel):
    name: str
    member_ids: List[int] = []

class SessionBase(BaseModel):
    dance_id: int
    duration: int
    custom_time: Optional[str] = None
    is_runthrough: bool = False

class ReorderPayload(BaseModel):
    order: List[int]

class DancerCreate(BaseModel):
    name: str

class DailyConstraintCreate(BaseModel):
    dancer_id: int
    time_range: str
