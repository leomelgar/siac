from flask import Flask
from routes.contacts import contacts
from routes.colegios import colegios
from routes.docentes import docentes
from routes.alumnos import alumnos
from routes.catedras import catedras
from routes.asignaturas import asignaturas
from routes.cursos import cursos
from routes.clases import clases
from flask_sqlalchemy import SQLAlchemy
from config import DATABASE_CONNECTION_URI

app = Flask(__name__)

# settings
app.secret_key = 'mysecret'
print(DATABASE_CONNECTION_URI)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_CONNECTION_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# no cache
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

SQLAlchemy(app)

app.register_blueprint(contacts)
app.register_blueprint(colegios)
app.register_blueprint(docentes)
app.register_blueprint(alumnos)
app.register_blueprint(catedras)
app.register_blueprint(asignaturas)
app.register_blueprint(cursos)
app.register_blueprint(clases)
