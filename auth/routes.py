from fastapi import APIRouter, HTTPException, Depends
from auth.models import User
from auth.schemas import UserSchema, LoginSchema
from sqlalchemy.orm import Session
from dependencies import dbSession, validateToken
from main import bcrypt_context, SECRET_KEY, ALGORITHM
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordRequestForm



auth_router = APIRouter(prefix="/auth", tags=["auth"])

def createToken(user, type: str, duration=timedelta(minutes=30)):
    expDate = datetime.now(timezone.utc) + duration

    if type == "refresh":
        dic_info = {"sub": str(user.id), "exp": expDate}
    else:
        dic_info = {"sub": str(user.id),
                    "name": user.name,
                    "admin": str(user.admin),
                    "type": type,
                      "exp": expDate}
    codedJwt = jwt.encode(dic_info, SECRET_KEY, ALGORITHM)
    return codedJwt

@auth_router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(dbSession)):
    user = session.query(User).filter(User.email==form.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    if not bcrypt_context.verify(form.password, user.password):
        raise HTTPException(status_code=401, detail=f"Login bem-sucedido para o usuário {form.username}")
    
    access_token = createToken(user, "access")
    refresh_token = createToken(user, "refresh", timedelta(days=7))
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer"
        }



@auth_router.post("/create")
async def createAccount(newUser: UserSchema, session: Session = Depends(dbSession)):
    user = session.query(User).filter(User.email==newUser.email).first()
    if user:
        # ja existe um usuario com esse email
        raise HTTPException(status_code=400, detail="E-mail do usuário já cadastrado")
    else:
        senha_criptografada = bcrypt_context.hash(newUser.password)
        newUserToAdd = User(newUser.name, newUser.email, senha_criptografada, newUser.active, newUser.admin)
        session.add(newUserToAdd)
        session.commit()
        return {"mensagem": f"usuário cadastrado com sucesso {newUser.email}"}

@auth_router.get("/refresh")
async def refreshToken(userFromToken = Depends(validateToken), session: Session = Depends(dbSession)):
    user = session.query(User).filter(User.id==userFromToken.get("id")).first()
    access_token = createToken(user, "access")
    return {
        "access_token": access_token,
        "token_type": "Bearer"
        }