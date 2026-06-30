""" from utils.db import db
class Colegio(db.Model):
    idColegios = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(45))
    direccion = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(200))
    docentes = db.relationship('Docente',backref='colegio', lazy='dynamic')
    matriculas = db.relationship('Matricula',backref='matricula', lazy='dynamic')

    def __init__(self, nombre, direccion, telefono, email):
        self.nombre=nombre
        self.direccion=direccion
        self.telefono=telefono
        self.email=email
    # def __repr__(self) -> str:
    #     return f'Colegio:{self.nombre,self.direcion,self.telefono,self.email}'

class Docente(db.Model):
    idDocente = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(45))
    apellido = db.Column(db.String(45))
    cuil = db.Column(db.String(15))
    direccion = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(200))
    colegio_id = db.Column(db.Integer, db.ForeignKey('colegio.idColegios'))
    cargaAcademica = db.relationship('Catedra',backref='cargaAcademica', lazy='dynamic')

    def __init__(self, nombre, apellido, cuil, direccion, telefono, email, colegio_id):
        self.nombre=nombre
        self.apellido=apellido
        self.cuil=cuil
        self.direccion=direccion
        self.telefono=telefono
        self.email=email
        self.colegio_id=colegio_id

class Tutor(db.Model):
    idTutor = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(45))
    apellido = db.Column(db.String(45))
    cuil = db.Column(db.String(15))
    parentesco = db.Column(db.String(8))
    direccion = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(200))
    alumnos = db.relationship('Alumno',backref='tutor', lazy='dynamic')

    def __init__(self, nombre, apellido, cuil, parentesco, direccion, telefono, email):
        self.nombre=nombre
        self.apellido=apellido
        self.cuil=cuil
        self.parentesco=parentesco
        self.direccion=direccion
        self.telefono=telefono
        self.email=email


class Alumno(db.Model):
    idAlumno = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(45))
    apellido = db.Column(db.String(45))
    cuil = db.Column(db.String(15))
    fechaNac = db.Column(db.Date)
    sexo = db.Column(db.String(10))
    direccion = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(200))
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutor.idTutor'))
    matricular = db.relationship('Matricula',backref='matricular', lazy='dynamic')

    def __init__(self, nombre, apellido, cuil, fechaNac, sexo, direccion, telefono, email, tutor_id):
        self.nombre=nombre
        self.apellido=apellido
        self.cuil=cuil
        self.fechaNac=fechaNac
        self.sexo=sexo
        self.direccion=direccion
        self.telefono=telefono
        self.email=email
        self.tutor_id=tutor_id

class Matricula(db.Model):
    idMatricula = db.Column(db.Integer, primary_key=True)
    fechaInscripcion = db.Column(db.Date) #fecha de alta del alumno, cuando se inscribe por primera vez en el colegio
    reInscripcion = db.Column(db.Date, nullable=True) #reinscripto-fecha en la cual se volvio a inscribir, para cursar otro año
    añoAcademico = db.Column(db.String(8), nullable=False)#el año que esta cursando el alumno
    condicionIngreso = db.Column(db.String(22), nullable=False)#ingresante a primer año o por pase de otro establecimiento
    #fechaEgreso = db.Column(db.Date, nullable=True)#fecha que sale del establecimiento-ya sea por promocion(finalizacion de estudios) o cambio de colegio
    alumno_id = db.Column(db.Integer, db.ForeignKey('alumno.idAlumno'))
    colegio_id = db.Column(db.Integer, db.ForeignKey('colegio.idColegios'), nullable=True)
    curso_id = db.Column(db.Integer, db.ForeignKey('curso.idCurso'))
    #curso_matricula = db.relationship('Curso', backref='curso_matricula', lazy='dynamic')

    def __init__(self, fechaInscripcion, reInscripcion, añoAcademico, condicionIngreso, alumno_id, colegio_id, curso_id):
        self.fechaInscripcion=fechaInscripcion
        self.reInscripcion=reInscripcion
        self.añoAcademico=añoAcademico
        self.condicionIngreso=condicionIngreso
        self.alumno_id=alumno_id
        self.colegio_id=colegio_id
        self.curso_id = curso_id

class Asignatura(db.Model):
    idAsignatura = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20))
    descripcion = db.Column(db.String(100))
    horasCatedra = db.relationship('Catedra',backref='horasCatedra', lazy='dynamic')

    def __init__(self, nombre, descripcion):
        self.nombre = nombre
        self.descripcion = descripcion

class Catedra(db.Model):
    idCatedra = db.Column(db.Integer, primary_key=True)
    nombre_cat = db.Column(db.String(20))
    cargaHoraria = db.Column(db.Float)   #cantidad de horas asignadas a la materia o asignatura
    tipoCargo = db.Column(db.String(16)) #docente, administrativo, profesional, tecnico
    caracter = db.Column(db.String(10))  #titural, interino, suplente
    asignatura_id = db.Column(db.Integer, db.ForeignKey('asignatura.idAsignatura'))
    docente_id = db.Column(db.Integer, db.ForeignKey('docente.idDocente'))
    fk_catedra_clase = db.relationship('Clase', backref='fk_fk_catedra_clase', lazy='dynamic')
    

    def __init__(self, nombre_cat, cargaHoraria, tipoCargo, caracter, asignatura_id, docente_id):
        self.nombre_cat=nombre_cat
        self.cargaHoraria=cargaHoraria
        self.tipoCargo=tipoCargo
        self.caracter=caracter
        self.asignatura_id=asignatura_id
        self.docente_id=docente_id

class Aula(db.Model):
    idAula = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(6))
    capacidad = db.Column(db.String(2))
    ubicacion = db.Column(db.String(10))
    curso_aula = db.relationship('Curso',backref='curso_aula', lazy='dynamic')

    def __init__(self, nombre, capacidad, ubicacion):
        self.nombre = nombre
        self.capacidad = capacidad
        self.ubicacion = ubicacion

class Horario(db.Model):
    idHorario = db.Column(db.Integer, primary_key=True)
    dia = db.Column(db.String(3))
    hora = db.Column(db.String(13))
    descripcion = db.Column(db.String(8))
    fk_horario_clase = db.relationship('Clase', backref='fk_horario_clase', lazy='dynamic')


    def __init__(self, dia, hora, descripcion):
        self.dia  = dia
        self.hora = hora
        self.descripcion = descripcion

class Turno(db.Model):
    idTurno = db.Column(db.Integer, primary_key=True)
    turno = db.Column(db.String(6))
    curso_turno = db.relationship('Curso', backref='curso_turno', lazy='dynamic')

    def __init__(self, turno):
        self.turno = turno

class Curso(db.Model):  
    idCurso = db.Column(db.Integer, primary_key=True)
    nombre_curso = db.Column(db.String(7), nullable=False)
    division = db.Column(db.String(7))
    periodo = db.Column(db.String(4))
    aula_id = db.Column(db.Integer, db.ForeignKey('aula.idAula'))
    turno_id = db.Column(db.Integer, db.ForeignKey('turno.idTurno'))
    curso_matricula = db.relationship('Matricula', backref='curso_matricula', lazy='dynamic')
    fk_clase = db.relationship('Clase', backref='fk_clase', lazy='dynamic')

    def __init__(self, nombre_curso, division, periodo, aula_id, turno_id):
        self.nombre_curso = nombre_curso
        self.division = division
        self.periodo = periodo
        self.aula_id = aula_id
        self.turno_id = turno_id

class Clase(db.Model):
    idClase = db.Column(db.Integer, primary_key=True)
    nombre_clase = db.Column(db.String(20))
    curso_id = db.Column(db.Integer, db.ForeignKey('curso.idCurso'))
    catedra_id = db.Column(db.Integer, db.ForeignKey('catedra.idCatedra'))
    horario_id = db.Column(db.Integer, db.ForeignKey('horario.idHorario'))

    def __init__(self, nombre_clase, curso_id, catedra_id, horario_id):
        self.nombre_clase = nombre_clase
        self.curso_id = curso_id
        self.catedra_id = catedra_id
        self.horario_id = horario_id
 """
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# --- Tablas Maestras ---

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
    observaciones = db.Column(db.Text)   