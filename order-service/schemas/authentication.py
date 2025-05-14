from pydantic import BaseModel

class LoginForm(BaseModel):
    login: str
    password: str

class LoginResponse(BaseModel):
    full_name: str
    token: str

