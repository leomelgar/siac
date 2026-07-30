from flask import Flask, Response
from flask_login import LoginManager
from routes.dashboard import colegio
from routes.colegios import colegios
from routes.docentes import docentes
from routes.alumnos import alumnos
from routes.asignaturas import asignaturas
from routes.aulas import aulas
from routes.auth import auth
from routes.matriculas import matricula_bp
from flask_sqlalchemy import SQLAlchemy
from config import DATABASE_CONNECTION_URI
from utils.db import db
from models.colege import Usuario
import urllib.parse

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    # settings
    app.config["SECRET_KEY"]='sisPruebaV1'
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_CONNECTION_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # no cache
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    db.init_app(app)

    # --- Filtros Jinja personalizados ---
    from utils.template_filters import register_filters
    register_filters(app)

     # --- Páginas de error propias (401, 403, 404) ---
    from utils.error_handlers import register_error_handlers
    register_error_handlers(app)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'          # blueprint 'auth', endpoint 'login'
    login_manager.login_message = 'Debés iniciar sesión para acceder a esta página.'
    login_manager.login_message_category = 'warning'

    app.register_blueprint(auth)
    app.register_blueprint(colegio)
    app.register_blueprint(colegios)
    app.register_blueprint(docentes)
    app.register_blueprint(alumnos)
    app.register_blueprint(matricula_bp)
    app.register_blueprint(asignaturas)
    app.register_blueprint(aulas)
    #app.register_blueprint(clases)

    with app.app_context():
        db.create_all()
    return app

@login_manager.user_loader
def load_user(id_usuario):
    # Flask-Login siempre pasa el id como string, por eso el int()
    return Usuario.query.get(int(id_usuario))


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host="0.0.0.0")

@app.route('/avatar/<username>')
def avatar_svg(username):
    # Solo letras/números para las iniciales
    limpio = re.sub(r'[^A-Za-zÁÉÍÓÚáéíóúÑñ0-9]', '', username or 'U')
    if not limpio:
        limpio = 'U'

    iniciales = limpio[:2].upper()

    colores = ["0d6efd", "198754", "dc3545", "fd7e14", "6f42c1", "20c997", "6610f2", "d63384"]
    color = colores[sum(ord(c) for c in limpio) % len(colores)]

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">
  <rect width="128" height="128" fill="#{color}"/>
  <text x="64" y="64"
        text-anchor="middle"
        dominant-baseline="central"
        fill="#ffffff"
        font-family="system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif"
        font-size="52"
        font-weight="700">{iniciales}</text>
</svg>'''

    return Response(svg, mimetype='image/svg+xml')