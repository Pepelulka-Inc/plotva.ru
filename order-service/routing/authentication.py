from fastapi import APIRouter
from schemas.authentication import LoginForm, LoginResponse

authentication = APIRouter(prefix='/auth', tags=['AUTH'])

@authentication.post('/login')

def login(login_data: LoginForm) -> LoginResponse:
    return LoginResponse()