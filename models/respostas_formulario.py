from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class RespostaFormulario(Base):
    __tablename__ = "respostas_formulario"

    id = Column(Integer, primary_key=True, index=True)
    id_formulario = Column(Integer, ForeignKey("formularios.id"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    respondido = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
