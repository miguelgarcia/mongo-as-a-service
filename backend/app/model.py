from datetime import datetime
from pydantic import BaseModel
import secrets
import string


class MongoInstance(BaseModel):
    name: str
    id: str | None = None
    created_at: datetime
    status: str | None = None
    host: str | None = None
    port: int | None = None

    @classmethod
    def generate_password(cls, length=16):
        characters = string.ascii_letters + string.digits
        return ''.join(secrets.choice(characters) for _ in range(length))