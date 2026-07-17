from pydantic import BaseModel, field_validator
from typing import Optional
from uuid import UUID

class MessageRequest(BaseModel):
    receiver_id: UUID
    content: str
    quote_id: Optional[UUID] = None

    @field_validator('content')  # ← indented inside class
    @classmethod
    def validate_content(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Message cannot be empty")
        if len(value) > 2000:
            raise ValueError("Message too long - max 2000 characters")
        return value
