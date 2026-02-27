from fastapi import APIRouter, HTTPException, Depends
from users.models import User
from sqlalchemy.orm import Session
from dependencies import dbSession, validateToken
from users.schemas import UserPublicSchema

users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.get("/me")
async def getMe(userFromToken = Depends(validateToken), session: Session = Depends(dbSession)):
    user: UserPublicSchema = session.query(User).filter(User.id==userFromToken.get("id")).first()
    return user

@users_router.get("/list")
async def listUsers(userFromToken = Depends(validateToken), session: Session = Depends(dbSession)):
    print(userFromToken)
    if not userFromToken.get("admin"):
        raise HTTPException(status_code=403, detail="Acesso negado")
    users: list[UserPublicSchema] = session.query(User).all()
    return users