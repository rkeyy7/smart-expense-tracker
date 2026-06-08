from app import db
from datetime import datetime

class Transaccion(db.Model):
    __tablename__ = 'transacciones'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(10), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    descripcion = db.Column(db.String(200))