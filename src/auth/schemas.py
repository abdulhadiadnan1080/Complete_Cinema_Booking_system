from pydantic import BaseModel

class AuthRequest(BaseModel):
    username: str
    password: str  

class ForgotPasswordRequest(BaseModel):
    username: str

class AuthResponse(BaseModel):
    username: str
    role: str
