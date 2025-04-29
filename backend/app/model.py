from datetime import datetime
from pydantic import BaseModel

class MongoInstance(BaseModel):
    name: str
    id: str
    created_at: datetime
    status: str | None = None
    host: str | None = None
    port: int | None = None