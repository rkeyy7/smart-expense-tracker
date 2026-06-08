from flask import request, jsonify
from app import app, db
from app.models import Transaccion

@app.route('/transacciones', methods=['POST'])
def crear_transaccion():
    data = request.get_json() # Obtenemos los datos que envía el usuario (en formato JSON)
    
    # Creamos un nuevo objeto (instancia) de nuestro modelo
    nueva_transaccion = Transaccion(
        tipo=data['tipo'],
        monto=data['monto'],
        categoria=data['categoria'],
        descripcion=data.get('descripcion', '') # .get es para que no falle si no envían descripción
    )
    
    # Guardamos en la base de datos
    db.session.add(nueva_transaccion)
    db.session.commit()
    
    return jsonify({"mensaje": "¡Transacción guardada con éxito!"}), 201


# METODO GET para obtener todas las transacciones

@app.route('/transacciones', methods=['GET'])
def obtener_transacciones():
    # Miramos si el usuario envió un parámetro llamado 'tipo' en la URL
    tipo_filtro = request.args.get('tipo') # Ejemplo: /transacciones?tipo=ingreso
    
    if tipo_filtro:
        # Filtramos si pidieron algo específico
        transacciones = Transaccion.query.filter_by(tipo=tipo_filtro).all()
    else:
        # Traemos todo si no pidieron filtro
        transacciones = Transaccion.query.all()
    
    # Convertimos los objetos de SQLAlchemy a una lista de diccionarios (JSON)
    lista_transacciones = []
    for t in transacciones:
        lista_transacciones.append({
            "id": t.id,
            "tipo": t.tipo,
            "monto": t.monto,
            "categoria": t.categoria,
            "descripcion": t.descripcion,
            "fecha": t.fecha.strftime('%Y-%m-%d') # Formateamos la fecha para que se vea bien
        })
    
    return jsonify(lista_transacciones), 200

# METODO DELETE para eliminar una transacción por su ID

@app.route('/transacciones/<int:id>', methods=['DELETE'])
def eliminar_transaccion(id):
    transaccion = Transaccion.query.get_or_404(id)
    db.session.delete(transaccion)
    db.session.commit()
    return jsonify({"mensaje": "Transacción eliminada correctamente"}), 200

# METODO PUT para actualizar una transacción por su ID

@app.route('/transacciones/<int:id>', methods=['PUT'])
def actualizar_transaccion(id):
    transaccion = Transaccion.query.get_or_404(id)
    data = request.get_json()
    
    transaccion.tipo = data.get('tipo', transaccion.tipo)
    transaccion.monto = data.get('monto', transaccion.monto)
    transaccion.categoria = data.get('categoria', transaccion.categoria)
    transaccion.descripcion = data.get('descripcion', transaccion.descripcion)
    
    db.session.commit()
    return jsonify({"mensaje": "Transacción actualizada correctamente"}), 200


# METODO GET para obtener un resumen de ingresos, gastos y balance neto

from sqlalchemy import func

@app.route('/resumen', methods=['GET'])
def obtener_resumen():
    # Sumamos los montos agrupados por tipo
    resultados = db.session.query(
        Transaccion.tipo, 
        func.sum(Transaccion.monto)
    ).group_by(Transaccion.tipo).all()
    
    # Transformamos el resultado en un formato fácil de leer
    resumen = {r[0]: r[1] for r in resultados}
    
    # Calculamos balance neto
    ingresos = resumen.get('ingreso', 0)
    gastos = resumen.get('gasto', 0)
    
    return jsonify({
        "ingresos_totales": ingresos,
        "gastos_totales": gastos,
        "balance_neto": ingresos - gastos
    }), 200