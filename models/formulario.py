from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from database import Base

class Formulario(Base):
    __tablename__ = "formularios"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(255), nullable=False)
    descricao = Column(Text)
    dt_abertura = Column(DateTime, nullable=False)
    dt_fechamento = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
