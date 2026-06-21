from pydantic import BaseModel

class SignupRequest(BaseModel):
  email: str
  password: str
  name: str
  role: str
  phone: str 
  
  
class LoginRequest(BaseModel):
  email: str
  password: str