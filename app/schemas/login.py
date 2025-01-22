from typing import List
from pydantic import BaseModel

class LoginOptions(BaseModel):
    """Schema for available login options."""
    options: List[str] = []
