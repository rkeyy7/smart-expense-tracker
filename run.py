from app import create_app, db

app = create_app()

# Esto crea las tablas si no existen antes de arrancar
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)