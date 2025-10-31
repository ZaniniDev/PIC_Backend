from sqlalchemy import Column, Integer, String, Date, DateTime
from datetime import datetime
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    id_hash = Column(String)
    level = Column(Integer, default=0)
    nome = Column(String)
    email = Column(String, unique=True, index=True)
    telefone = Column(String, unique=True, index=True, nullable=False)
    data_nascimento = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    bairro = Column(String)
    cidade = Column(String)
    estado = Column(String)
    cep = Column(String)
    rua = Column(String)
