from flask import Flask
from flask_login import LoginManager
from routes.dashboard import colegio
from routes.colegios import colegios
from routes.docentes import docentes
from routes.alumnos import alumnos
from routes.asignaturas import asignaturas
from routes.aulas import aulas
from routes.auth import auth
from flask_sqlalchemy import SQLAlchemy
from config import DATABASE_CONNECTION_URI
from utils.db import db
from models.colege import Usuario

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    # settings
    app.config["SECRET_KEY"]
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_CONNECTION_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # no cache
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    db.init_app(app)
    #db = SQLAlchemy(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'          # blueprint 'auth', endpoint 'login'
    login_manager.login_message = 'Debés iniciar sesión para acceder a esta página.'
    login_manager.login_message_category = 'warning'

    app.register_blueprint(auth)
    app.register_blueprint(colegio)
    app.register_blueprint(colegios)
    app.register_blueprint(docentes)
    app.register_blueprint(alumnos)
    #app.register_blueprint(catedras)
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

#https://search.brave.com/ask?q=dise%C3%B1a+una+base+de+datos+relacional+para+un+colegio%2C+usando+como+entidades%3A+docentes%2C+alumnos%2C+tutores+o+padres%2C+clases%2C+asignaturas%2C+asistencias%2C+aulas%2C+horarios%2C+turnos%2C+matricula&conversation=09449ab4044c71666cff6ccdde0d74f5d65e#tsD7lfqaHop5ZTDXkvXYHRKniXz_ZLZG_QRNdwlWZSw