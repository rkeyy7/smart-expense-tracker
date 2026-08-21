from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os

app = Flask(__name__)

# --- CONFIGURACIÓN DE CORS LIMPIA Y CORRECTA ---
# Una sola llamada, permitiendo a Vercel conectarse sin conflictos de seguridad
CORS(app, resources={r"/*": {"origins": "*"}})

# Leemos la clave desde Render, o usamos la tuya por defecto
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "rkeyy7")
jwt = JWTManager(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:rkeyy7@localhost:5432/smart_expense_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Importamos las rutas al final para evitar circular imports
from app import routes