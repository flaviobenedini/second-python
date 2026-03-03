from fastapi import APIRouter, HTTPException, Depends
from users.models import User
from auth.schemas import UserSchema, LoginSchema
from sqlalchemy.orm import Session
from dependencies import dbSession, validateToken, emailSession
from main import bcrypt_context, WEB_CLIENT_ID, SECRET_KEY, ALGORITHM
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordRequestForm
from email.mime.text import MIMEText
from google.oauth2 import id_token
from google.auth.transport import requests
from pydantic import BaseModel

class GoogleLogin(BaseModel):
    credential: str

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

def createTokenToResetPassword(user):
    expDate = datetime.now(timezone.utc) + timedelta(days=1)
    dic_info = {"sub": str(user.id), "exp": expDate, "type": "reset_password"}
    codedJwt = jwt.encode(dic_info, SECRET_KEY, ALGORITHM)
    return codedJwt

@auth_router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(dbSession)):
    user = session.query(User).filter(User.email==form.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    if user.google_auth:
        raise HTTPException(status_code=401, detail=f"Esse usuário deve fazer login usando o Google")
    if not bcrypt_context.verify(form.password, user.password):
        raise HTTPException(status_code=401, detail=f"Login bem-sucedido para o usuário {form.username}")
    
    access_token = createToken(user, "access")
    refresh_token = createToken(user, "refresh", timedelta(days=7))
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer"
        }

@auth_router.post("/google-login")
async def googleAuth(data: GoogleLogin, session: Session = Depends(dbSession)):

    credential = data.credential

    try:
        credentialInfo = id_token.verify_oauth2_token(credential, requests.Request(), WEB_CLIENT_ID)
        userId = credentialInfo['sub']
        email = credentialInfo['email']
        name = credentialInfo['name']

        user = session.query(User).filter(User.email==email, User.google_auth_id==userId).first()

        if not user:
            newUser = User(
                name=name,
                email=email,
                password="",
                google_auth_id=userId,
                active=True,
                admin=False,
                google_auth=True) 
            session.add(newUser)
            session.commit()
            user = newUser

        access_token = createToken(user, "access")
        refresh_token = createToken(user, "refresh", timedelta(days=7))
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer"
            }
    except ValueError:
        return HTTPException(status_code=400, detail="Token do Google inválido")
    except Exception as e:
        print(f"An error occurred: {e}")



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

@auth_router.post("/recovery")
async def recoveryPassword(email: str, session: Session = Depends(dbSession), servidorEmail = Depends(emailSession)):
    user = session.query(User).filter(User.email==email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    if user.google_auth:
        raise HTTPException(status_code=401, detail="Usuário cadastrado com Google Auth não pode recuperar senha")
    
    recoveryToken = createTokenToResetPassword(user)
    sender = 'flaviobenedini.dev@gmail.com'
    receiver = email

    body = MIMEText(f"Para recuperar sua senha, clique no link: http://localhost:3000/reset-password?token={recoveryToken}")
    body['Subject'] = "Test Email"
    body['From'] = sender
    body['To'] = receiver

    servidorEmail.sendmail(sender, receiver, body.as_string())
    return {"mensagem": f"Se o e-mail {email} estiver cadastrado, um link de recuperação de senha será enviado."}

@auth_router.post("/reset-password")
async def resetPassword(newPassword: str, token: str, session: Session = Depends(dbSession)):
    try:
        dic_info = jwt.decode(token, SECRET_KEY, ALGORITHM)
        if dic_info.get("type") != "reset_password":
            raise HTTPException(status_code=400, detail="Token inválido para recuperação de senha")
        user_id = int(dic_info.get("sub"))
    except JWTError:
        raise HTTPException(status_code=400, detail="Token de recuperação de senha inválido ou expirado")

    user = session.query(User).filter(User.id==user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    user.password = bcrypt_context.hash(newPassword)
    session.commit()
    return {"mensagem": "Senha atualizada com sucesso"}