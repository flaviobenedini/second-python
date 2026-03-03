from fastapi import FastAPI
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
GMAIL_SMTP_SERVER = os.getenv("GMAIL_SMTP_SERVER")
GMAIL_SMTP_PORT = os.getenv("GMAIL_SMTP_PORT")
GMAIL_USERNAME = os.getenv("GMAIL_USERNAME")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")
WEB_CLIENT_ID = os.getenv("WEB_CLIENT_ID")

origins = [
    "http://localhost:3000", # Default Next.js development port
    # Add your production frontend URL here when deploying
    # "https://your-nextjs-app-domain.com", 
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,  # Set to True if you use cookies/auth headers
    allow_methods=["*"],     # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],     # Allows all headers, including custom headers
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login")

from auth.routes import auth_router
app.include_router(auth_router)
from users.routes import users_router
app.include_router(users_router)
from groups.routes import groups_router
app.include_router(groups_router)
