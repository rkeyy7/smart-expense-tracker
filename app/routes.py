from flask import request, jsonify
from . import app, db 
from .models import Transaccion, User
from datetime import datetime, timedelta
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token

# 1. BYPASS DE CORS PARA JWT
@app.before_request
def handle_preflight():
    if request.method == 'OPTIONS':
        return '', 200

# 2. RUTAS DE AUTENTICACIÓN (Las que se habían borrado)
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "El usuario ya existe"}), 400
    
    nuevo_usuario = User(email=data['email'])
    nuevo_usuario.set_password(data['password'])
    db.session.add(nuevo_usuario)
    db.session.commit()
    return jsonify({"message": "Usuario registrado exitosamente"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    usuario = User.query.filter_by(email=data.get('email')).first()
    
    if usuario and usuario.check_password(data.get('password')):
        # Creamos el token válido por 24 horas
        access_token = create_access_token(identity=str(usuario.id), expires_delta=timedelta(hours=24))
        return jsonify({
            "message": "Inicio de sesión exitoso", 
            "access_token": access_token
        }), 200
    
    return jsonify({"message": "Credenciales inválidas"}), 401

# 3. RUTAS PROTEGIDAS (Transacciones y Gráficos)
@app.route('/transacciones', methods=['GET'])
@jwt_required()
def obtener_transacciones():
    user_id = get_jwt_identity() 
    transacciones = Transaccion.query.filter_by(user_id=user_id).all()
    
    lista = [{
        "id": t.id,
        "tipo": t.tipo,
        "monto": t.monto,
        "categoria": t.categoria,
        "descripcion": t.descripcion,
        "fecha": t.fecha.strftime('%Y-%m-%d') if t.fecha else None
    } for t in transacciones]
    return jsonify(lista), 200

@app.route('/transacciones', methods=['POST'])
@jwt_required()
def crear_transaccion():
    user_id = get_jwt_identity()
    data = request.get_json()
    nueva = Transaccion(
        tipo=data['tipo'],
        monto=data['monto'],
        categoria=data['categoria'],
        descripcion=data.get('descripcion', ''),
        fecha=datetime.strptime(data['fecha'], '%Y-%m-%d') if data.get('fecha') else datetime.utcnow(),
        user_id=user_id 
    )
    db.session.add(nueva)
    db.session.commit()
    return jsonify({"mensaje": "¡Guardado!"}), 201

@app.route('/transacciones/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_transaccion(id):
    user_id = get_jwt_identity()
    transaccion = Transaccion.query.filter_by(id=id, user_id=user_id).first_or_404()
    db.session.delete(transaccion)
    db.session.commit()
    return jsonify({"mensaje": "Eliminado"}), 200

@app.route('/transacciones/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar_transaccion(id):
    user_id = get_jwt_identity()
    transaccion = Transaccion.query.filter_by(id=id, user_id=user_id).first_or_404()
    data = request.get_json()
    
    transaccion.tipo = data.get('tipo', transaccion.tipo)
    transaccion.monto = data.get('monto', transaccion.monto)
    transaccion.categoria = data.get('categoria', transaccion.categoria)
    transaccion.descripcion = data.get('descripcion', transaccion.descripcion)
    
    db.session.commit()
    return jsonify({"mensaje": "Actualizado"}), 200

@app.route('/api/gastos-por-categoria', methods=['GET'])
@jwt_required()
def get_gastos_por_categoria():
    user_id = get_jwt_identity()
    from sqlalchemy import func
    resultados = db.session.query(Transaccion.categoria, func.sum(Transaccion.monto))\
        .filter(Transaccion.user_id == user_id, Transaccion.tipo == 'gasto')\
        .group_by(Transaccion.categoria).all()
    return jsonify([{"name": r[0], "value": float(r[1])} for r in resultados]), 200

@app.route('/api/ingresos-por-categoria', methods=['GET'])
@jwt_required()
def get_ingresos_por_categoria():
    user_id = get_jwt_identity()
    from sqlalchemy import func
    resultados = db.session.query(Transaccion.categoria, func.sum(Transaccion.monto))\
        .filter(Transaccion.user_id == user_id, Transaccion.tipo == 'ingreso')\
        .group_by(Transaccion.categoria).all()
    return jsonify([{"name": r[0], "value": float(r[1])} for r in resultados]), 200

# Verificador para consola
print("\n--- RUTAS ACTIVAS ---")
for rule in app.url_map.iter_rules():
    print(f"{rule.endpoint}: {rule.rule}")
print("---------------------\n")