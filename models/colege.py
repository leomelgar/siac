#Relaciones: El uso de db.ForeignKey define la clave foránea en la base de datos, 
#mientras que db.relationship permite acceder a los datos relacionados 
#como atributos de objeto en Python (ej. alumno.tutor). 
#from flask_sqlalchemy import SQLAlchemy
from utils.db import db
from datetime import datetime

#db = SQLAlchemy()

""" # --- Tablas Maestras ---

class Turno(db.Model):
    __tablename__ = 'turnos'
    id_turno = db.Column(db.Integer, primary_key=True)
    nombre_turno = db.Column(db.String(50), nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    
    # Relación
    clases = db.relationship('Clase', backref='turno', lazy=True)

class Aula(db.Model):
    __tablename__ = 'aulas'
    id_aula = db.Column(db.Integer, primary_key=True)
    nombre_aula = db.Column(db.String(50), nullable=False)
    capacidad = db.Column(db.Integer)
    ubicacion = db.Column(db.String(100))

    # Relación
    horarios = db.relationship('Horario', backref='aula', lazy=True)

class Tutor(db.Model):
    __tablename__ = 'tutores'
    id_tutor = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    direccion = db.Column(db.Text)

    # Relación uno a muchos con Alumnos
    alumnos = db.relationship('Alumno', backref='tutor', lazy=True)

class Docente(db.Model):
    __tablename__ = 'docentes'
    id_docente = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    especialidad = db.Column(db.String(100))
    email = db.Column(db.String(100))
    telefono = db.Column(db.String(20))

    # Relaciones
    clases_tutoradas = db.relationship('Clase', backref='docente_tutor', lazy=True)
    horarios_asignados = db.relationship('Horario', backref='docente', lazy=True)

class Alumno(db.Model):
    __tablename__ = 'alumnos'
    id_alumno = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    fecha_nacimiento = db.Column(db.Date)
    id_tutor = db.Column(db.Integer, db.ForeignKey('tutores.id_tutor'), nullable=False)
    direccion = db.Column(db.Text)

    # Relación muchos a muchos con Clases a través de Matricula
    matriculas = db.relationship('Matricula', backref='alumno', lazy=True)

class Asignatura(db.Model):
    __tablename__ = 'asignaturas'
    id_asignatura = db.Column(db.Integer, primary_key=True)
    nombre_asignatura = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    creditos = db.Column(db.Integer)

    # Relación
    horarios = db.relationship('Horario', backref='asignatura', lazy=True)

# --- Tablas de Estructura Académica ---

class Clase(db.Model):
    __tablename__ = 'clases'
    id_clase = db.Column(db.Integer, primary_key=True)
    nombre_clase = db.Column(db.String(50), nullable=False) # Ej: "1º A"
    nivel_academico = db.Column(db.String(50))
    id_docente_tutor = db.Column(db.Integer, db.ForeignKey('docentes.id_docente'))
    id_turno = db.Column(db.Integer, db.ForeignKey('turnos.id_turno'))

    # Relaciones
    matriculas = db.relationship('Matricula', backref='clase', lazy=True)
    horarios = db.relationship('Horario', backref='clase', lazy=True)

class Horario(db.Model):
    __tablename__ = 'horarios'
    id_horario = db.Column(db.Integer, primary_key=True)
    id_clase = db.Column(db.Integer, db.ForeignKey('clases.id_clase'), nullable=False)
    id_asignatura = db.Column(db.Integer, db.ForeignKey('asignaturas.id_asignatura'), nullable=False)
    id_docente = db.Column(db.Integer, db.ForeignKey('docentes.id_docente'), nullable=False)
    id_aula = db.Column(db.Integer, db.ForeignKey('aulas.id_aula'), nullable=False)
    dia_semana = db.Column(db.String(15), nullable=False) # Ej: 'Lunes'
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)

    # Relación
    asistencias = db.relationship('Asistencia', backref='horario', lazy=True)

# --- Tablas Transaccionales ---
#Una Clase tiene Muchos Alumnos (vía Matrícula): 
#La relación es N:M entre Alumnos y Clases, resuelta por la tabla intermedia Matricula. 

class Matricula(db.Model):
    __tablename__ = 'matriculas'
    id_matricula = db.Column(db.Integer, primary_key=True)
    id_alumno = db.Column(db.Integer, db.ForeignKey('alumnos.id_alumno'), nullable=False)
    id_clase = db.Column(db.Integer, db.ForeignKey('clases.id_clase'), nullable=False)
    fecha_matricula = db.Column(db.Date, default=datetime.utcnow)
    periodo_academico = db.Column(db.String(20)) # Ej: "2026-2027"
    estado = db.Column(db.String(20), default='Activa')

    # Relación
    asistencias = db.relationship('Asistencia', backref='matricula', lazy=True)

class Asistencia(db.Model):
    __tablename__ = 'asistencias'
    id_asistencia = db.Column(db.Integer, primary_key=True)
    id_matricula = db.Column(db.Integer, db.ForeignKey('matriculas.id_matricula'), nullable=False)
    id_horario = db.Column(db.Integer, db.ForeignKey('horarios.id_horario'), nullable=True)
    fecha = db.Column(db.Date, nullable=False)
    estado = db.Column(db.String(20), nullable=False) # Presente, Ausente, Tardanza
    observaciones = db.Column(db.Text)   """ 

#Relaciones (db.relationship y db.ForeignKey):
#Uno a Muchos (1:N): Se define con db.ForeignKey en la tabla "hija" 
#(ej. id_colegio en Docente) y db.relationship en la tabla "padre" (Colegio). 
#Esto permite acceder a colegio.docentes para obtener una lista de todos los docentes.
#Integridad: Al definir nullable=False en las claves foráneas, garantizamos que no se 
#pueda crear un alumno sin un colegio o tutor asignado.


class Colegio(db.Model):
    __tablename__ = 'colegio'
    id_colegio = db.Column(db.Integer, primary_key=True)
    nombre_colegio = db.Column(db.String(150), nullable=False)
    codigo_dane = db.Column(db.String(50), unique=True)
    direccion = db.Column(db.Text)
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    
    # Relaciones
    docentes = db.relationship('Docente', backref='colegio', lazy=True)
    alumnos = db.relationship('Alumno', backref='colegio', lazy=True)
    aulas = db.relationship('Aula', backref='colegio', lazy=True)
    asignaturas = db.relationship('Asignatura', backref='colegio', lazy=True)

class Tutor(db.Model):
    __tablename__ = 'tutores'
    id_tutor = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    direccion = db.Column(db.Text)
    
    alumnos = db.relationship('Alumno', backref='tutor', lazy=True)

class Docente(db.Model):
    __tablename__ = 'docentes'
    id_docente = db.Column(db.Integer, primary_key=True)
    id_colegio = db.Column(db.Integer, db.ForeignKey('colegio.id_colegio'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    especialidad = db.Column(db.String(100))
    email = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    def __init__(self, id_colegio, nombre, especialidad, email, telefono)
        self.id_colegio = id_colegio
        self.nombre = nombre
        self.especialidad = especialidad
        self.email = email
        self.telefono = telefono

class Alumno(db.Model):
    __tablename__ = 'alumnos'
    id_alumno = db.Column(db.Integer, primary_key=True)
    id_colegio = db.Column(db.Integer, db.ForeignKey('colegio.id_colegio'), nullable=False)
    id_tutor = db.Column(db.Integer, db.ForeignKey('tutores.id_tutor'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    fecha_nacimiento = db.Column(db.Date)
    direccion = db.Column(db.Text)

class Asignatura(db.Model):
    __tablename__ = 'asignaturas'
    id_asignatura = db.Column(db.Integer, primary_key=True)
    id_colegio = db.Column(db.Integer, db.ForeignKey('colegio.id_colegio'), nullable=False)
    nombre_asignatura = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    creditos = db.Column(db.Integer)
    def __init__(self, id_colegio, nombre_asignatura, descripcion, creditos):
        self.id_colegio = id_colegio
        self.nombre_asignatura = nombre_asignatura
        self.descripcion = descripcion
        self.creditos = creditos

class Aula(db.Model):
    __tablename__ = 'aulas'
    id_aula = db.Column(db.Integer, primary_key=True)
    id_colegio = db.Column(db.Integer, db.ForeignKey('colegio.id_colegio'), nullable=False)
    nombre_aula = db.Column(db.String(50), nullable=False)
    capacidad = db.Column(db.Integer)
    ubicacion = db.Column(db.String(100))

class Turno(db.Model):
    __tablename__ = 'turnos'
    id_turno = db.Column(db.Integer, primary_key=True)
    # Opcional: id_colegio si los turnos varían por sede
    nombre_turno = db.Column(db.String(50), nullable=False) 
    hora_inicio = db.Column(db.Time)
    hora_fin = db.Column(db.Time)

# ==========================================
# 2. MODELOS DE ESTRUCTURA Y TRANSACCIÓN
# ==========================================

class Clase(db.Model):
    __tablename__ = 'clases'
    id_clase = db.Column(db.Integer, primary_key=True)
    id_colegio = db.Column(db.Integer, db.ForeignKey('colegio.id_colegio'), nullable=False)
    id_docente_tutor = db.Column(db.Integer, db.ForeignKey('docentes.id_docente'), nullable=False)
    id_turno = db.Column(db.Integer, db.ForeignKey('turnos.id_turno'))
    nombre_clase = db.Column(db.String(50), nullable=False)
    nivel_academico = db.Column(db.String(50))
    
    # Relación con el objeto docente tutor
    docente_tutor_rel = db.relationship('Docente', foreign_keys=[id_docente_tutor])

class Horario(db.Model):
    __tablename__ = 'horarios'
    id_horario = db.Column(db.Integer, primary_key=True)
    id_clase = db.Column(db.Integer, db.ForeignKey('clases.id_clase'), nullable=False)
    id_asignatura = db.Column(db.Integer, db.ForeignKey('asignaturas.id_asignatura'), nullable=False)
    id_docente = db.Column(db.Integer, db.ForeignKey('docentes.id_docente'), nullable=False)
    id_aula = db.Column(db.Integer, db.ForeignKey('aulas.id_aula'), nullable=False)
    dia_semana = db.Column(db.String(15), nullable=False) # Ej: 'Lunes'
    hora_inicio = db.Column(db.Time)
    hora_fin = db.Column(db.Time)

class Matricula(db.Model):
    __tablename__ = 'matricula'
    id_matricula = db.Column(db.Integer, primary_key=True)
    id_alumno = db.Column(db.Integer, db.ForeignKey('alumnos.id_alumno'), nullable=False)
    id_clase = db.Column(db.Integer, db.ForeignKey('clases.id_clase'), nullable=False)
    fecha_matricula = db.Column(db.Date, default=datetime.utcnow)
    periodo_academico = db.Column(db.String(20))
    estado = db.Column(db.String(20), default='Activa')

class Asistencia(db.Model):
    __tablename__ = 'asistencias'
    id_asistencia = db.Column(db.Integer, primary_key=True)
    id_matricula = db.Column(db.Integer, db.ForeignKey('matricula.id_matricula'), nullable=False)
    id_horario = db.Column(db.Integer, db.ForeignKey('horarios.id_horario'))
    fecha = db.Column(db.Date, nullable=False)
    estado = db.Column(db.String(20)) # Presente, Ausente, etc.
    observaciones = db.Column(db.Text)