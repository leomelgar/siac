from utils.db import db
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

    def __init__(self, fechaInscripcion, reInscripcion, añoAcademico, condicionIngreso, alumno_id, colegio_id):
        self.fechaInscripcion=fechaInscripcion
        self.reInscripcion=reInscripcion
        self.añoAcademico=añoAcademico
        self.condicionIngreso=condicionIngreso
        self.alumno_id=alumno_id
        self.colegio_id=colegio_id

class Asignatura(db.Model):
    idAsignatura = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20))
    descripcion = db.Column(db.String(50))
    horasCatedra = db.relationship('Catedra',backref='horasCatedra', lazy='dynamic')

    def __init__(self, nombre, descripcion):
        self.nombre = nombre
        self.descripcion = descripcion

class Catedra(db.Model):
    idCatedra = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(16))
    cargaHoraria = db.Column(db.Float)   #cantidad de horas asignadas a la materia o asignatura
    tipoCargo = db.Column(db.String(16)) #docente, administrativo, profesional, tecnico
    caracter = db.Column(db.String(10))  #titural, interino, suplente
    asignatura_id = db.Column(db.Integer, db.ForeignKey('asignatura.idAsignatura'))
    docente_id = db.Column(db.Integer, db.ForeignKey('docente.idDocente'))

    def __init__(self, nombre, cargaHoraria, tipoCargo, caracter, asignatura_id, docente_id):
        self.nombre=nombre
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

    def __init__(self, nombre, capacidad, ubicacion):
        self.nombre = nombre
        self.capacidad = capacidad
        self.ubicacion = ubicacion
