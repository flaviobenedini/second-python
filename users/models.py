from models import Base
from sqlalchemy import Column, String, Integer, Boolean,Table, ForeignKey
from sqlalchemy.orm import deferred, relationship
from groups.models import groups_users
# criar as classes/tabelas do banco
class User(Base):
    __tablename__ = "users"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    email = Column("email", String, nullable=False)
    password = deferred(Column("password", String))
    name = Column("name", String)
    active = Column("active", Boolean)
    admin = Column("admin", Boolean, default=False)
    google_auth = Column("google_auth", Boolean, default=False)
    google_auth_id = Column("google_auth_id", String, nullable=True)
    groups = relationship("Group", secondary=groups_users, back_populates="users", lazy='subquery')

    def __init__(self, name, email, password, google_auth_id, active=True, admin=False, google_auth=False):
        self.name = name
        self.email = email
        self.password = password
        self.active = active
        self.admin = admin
        self.google_auth = google_auth
        self.google_auth_id = google_auth_id
    
