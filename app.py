# Autoras: Paola Camacho y Andrea Correa
from flask import Flask, render_template, redirect, url_for
from config import Config
from models import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    app.jinja_env.globals.update( #motor de Flask para renderizar HTML
        enumerate = enumerate,
        zip = zip,
        len = len,
        max = max,
        min = min,
    )

    #Blueprints
    from routes.sql_console import sql_bp #Consola SQL
    from routes.tablas import tablas_bp #CRUD
    from routes.joins import joins_bp #JOINS
    from routes.principales import principales_bp #Tablas sin FK

    app.register_blueprint(sql_bp, url_prefix='/sql')
    app.register_blueprint(tablas_bp, url_prefix='/tablas')
    app.register_blueprint(joins_bp, url_prefix='/joins')
    app.register_blueprint(principales_bp, url_prefix='/principales')


    @app.route('/')
    def index():
        #Obtener estadísticas de la base de datos, vista rapida de algunas tablas principales
        stats = {}
        try:
            from sqlalchemy import text
            tablas_conteo=[
                ("PACIENTES", "Pacientes"),
                ("PROFESIONALES", "Profesionales"),
                ("CITAS", "Citas"),
                ("HISTORIAS_CLINICAS", "HistoriasClinicas"),
                ("DIAGNOSTICOS", "Diagnosticos"),
                ("TRATAMIENTOS", "Tratamientos"),
                ("CONSULTORIOS", "Consultorios"),
            ]
            for tabla, label in tablas_conteo:
                try:
                    resultado = db.session.execute(text(f"SELECT COUNT(*) FROM {tabla}")).scalar()
                    stats[label] = resultado
                except Exception:
                    stats[label] = "No se pudo obtener el conteo"

        except Exception:
            pass
        return render_template('index.html', stats=stats)
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
