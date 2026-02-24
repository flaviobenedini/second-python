from fastapi import FastAPI
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = "RCn+1xN2x12pOxT5Atxtcm72sJhIEQVHz5m3Q/Lxqtg="
ALGORITHM = "HS256"

app = FastAPI()

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login")

from auth.routes import auth_router 

app.include_router(auth_router)