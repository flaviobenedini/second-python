from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
# from sqlalchemy_utils.types import ChoiceType

# cria a conexão do seu banco
db = create_engine("postgresql://postgres:postgres@127.0.0.1:5432/second")   

# cria a base do banco de dados
Base = declarative_base()

# criar as classes/tabelas do banco
class User(Base):
    __tablename__ = "users"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    email = Column("email", String, nullable=False)
    password = Column("password", String)
    name = Column("name", String)
    ativo = Column("active", Boolean)
    admin = Column("admin", Boolean, default=False)

    def __init__(self, name, email, password, active=True, admin=False):
        self.name = name
        self.email = email
        self.password = password
        self.active = active
        self.admin = admin
    
