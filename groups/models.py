from models import Base
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship

groups_users = Table('groups_users', Base.metadata,
    Column('group_id', Integer, ForeignKey('groups.id')),
    Column('user_id', Integer, ForeignKey('users.id'))
)


class Group(Base):
    __tablename__ = "groups"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String, nullable=False)
    description = Column("description", String)
    active = Column("active", Boolean)
    users = relationship("User", secondary=groups_users, back_populates="groups", lazy='subquery')


    def __init__(self, name, description, active=True):
        self.name = name
        self.description = description
        self.active = active
    


# class GroupUser(Base):
#     __tablename__ = "groups_users"

#     id = Column("id", Integer, primary_key=True, autoincrement=True)
#     group_id = Column("group_id", Integer, ForeignKey("groups.id"))
#     user_id = Column("user_id", Integer, ForeignKey("users.id"))

#     def __init__(self, group_id, user_id):
#         self.group_id = group_id
#         self.user_id = user_id