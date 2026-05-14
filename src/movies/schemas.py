from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MovieCreate(BaseModel):
    name: str
    duration_minutes: int
    start_time: datetime

class MovieResponse(BaseModel):
    movie_id: int
    movie_name: str
    duration_minutes: int
    start_time: datetime
    end_time: datetime

class SeatResponse(BaseModel):
    seat_id: int
    row_label: str
    seat_number: int
    is_booked: bool
    price: float
    booked_at: Optional[datetime] = None
    username: Optional[str] = None
