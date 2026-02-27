from fastapi import Depends, HTTPException
from models import db
from sqlalchemy.orm import sessionmaker
from main import oauth2_schema, SECRET_KEY, ALGORITHM
from jose import jwt, JWTError

def dbSession():
    try:
        Session = sessionmaker(bind=db)
        session = Session()
        yield session
    finally:
        session.close()

def validateToken(token: str = Depends(oauth2_schema)):
    try:
        dic_info = jwt.decode(token, SECRET_KEY, ALGORITHM)
        if dic_info.get("admin") == "True":
            dic_info["admin"] = True
        else:
            dic_info["admin"] = False
        user = {"id": int(dic_info.get("sub")), "name": dic_info.get("name"), "admin": dic_info.get("admin")}
    except JWTError:
        raise HTTPException(status_code=401, detail="Acesso Negado, verifique a validade do token")
    if not user:
        raise HTTPException(status_code=401, detail="Acesso Inválido")
    return user