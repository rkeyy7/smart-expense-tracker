from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuración (pon tu contraseña real aquí)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:rkeyy7@localhost:5432/smart_expense_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from app import routes