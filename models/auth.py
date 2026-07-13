from pydantic import BaseModel, field_validator
import phonenumbers
from phonenumbers import NumberParseException
import re

class BaseAuthRequest(BaseModel):
  email: str
  password: str
  
  @field_validator('email')
  @classmethod
  def validation_email(cls, value):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
      raise ValueError("Invalid email format")
    return value

class SignupRequest(BaseAuthRequest):
  full_name: str
  role: str
  phone_number: str 
  
  @field_validator('full_name')
  @classmethod
  def validation_full_name(cls, value):
    if len(value) < 3:
      raise ValueError('Username must be at least 3 characters')
    return value
  
  @field_validator('password')
  @classmethod
  def validation_password(cls, value):
    if len(value) < 6:
      raise ValueError("Password must be at least 6 characters")
    return value
  
  @field_validator('role')
  @classmethod
  def validation_role(cls, value):
    if value not in ['homeowner', 'contractor', 'architect']:
      raise ValueError("Role must be 'homeowner', 'contractor', or 'architect'")
    return value
  
  @field_validator('phone_number')
  @classmethod
  def validate_phone(cls, value):
    try:
      parsed = phonenumbers.parse(value, "KH")
      if not phonenumbers.is_valid_number(parsed):
        raise ValueError("Invalid phone number")
      return value
    except NumberParseException:
      raise ValueError("Phone number format is invalid. Example: 012345689 or +85512345689 ")
      
  
class LoginRequest(BaseAuthRequest):
  pass #everything handled in BaseAuthRequest