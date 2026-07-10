from pydantic import BaseModel, field_validator
from typing import Optional

class MessageRequest(BaseModel):
    receiver_id: str
    content: str
    quote_id: Optional[str] = None

    @field_validator('content')  # ← indented inside class
    @classmethod
    def validate_content(cls, value):
        if not value or len(value.strip()) == 0:
            raise ValueError("Message cannot be empty")
        if len(value) > 2000:
            raise ValueError("Message too long - max 2000 characters")
        return value 