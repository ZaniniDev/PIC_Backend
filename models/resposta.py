from sqlalchemy import Column, Integer, String, Date, DateTime
from datetime import datetime
from database import Base

class Resposta(Base):
    __tablename__ = "respostas"

    id = Column(Integer, primary_key=True, index=True)
    id_hash = Column(String)
    id_formulario = Column(String)
    id_usuario = Column(Integer)
    pergunta = Column(String)
    tipo_pergunta = Column(String)
    resposta = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
