from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

# cria a conexão do seu banco
db = create_engine("postgresql://postgres:postgres@127.0.0.1:5432/second")   

# cria a base do banco de dados
Base = declarative_base()

