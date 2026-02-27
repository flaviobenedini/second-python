from fastapi import APIRouter, HTTPException, Depends
from groups.models import Group
from sqlalchemy.orm import Session
from dependencies import dbSession, validateToken

groups_router = APIRouter(prefix="/groups", tags=["Groups"])

@groups_router.get("/list")
async def listGroups(userFromToken = Depends(validateToken), session: Session = Depends(dbSession)):
    if not userFromToken.get("admin"):
        raise HTTPException(status_code=403, detail="Acesso negado")
    groups: list[Group] = session.query(Group).all()
    return groups