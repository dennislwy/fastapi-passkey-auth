from pydantic import BaseModel

class Health(BaseModel):
    status: str
    version: str
    up_since: str
