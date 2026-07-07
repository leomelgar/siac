from utils.db import db
from datetime import datetime
"""# TABLA INTERMEDIA (Muchos a Muchos entre Alumno y Tutor)
alumno_tutor = db.Table('alumno_tutor',
    db.Column('alumno_id', db.Integer, db.ForeignKey('alumno.id', ondelete='CASCADE'), primary_key=True),
    db.Column('tutor_id', db.Integer, db.ForeignKey('tutor.id', ondelete='CASCADE'), primary_key=True)
)

class Colegio(db.Model):
    __tablename__ = 'colegio'
    id_colegio = db.Column(db.Integer, primary_key=True)
    nombre_colegio = db.Column(db.String(150), nullable=False)
    codigo_dane = db.Column(db.String(50), unique=True)
    direccion = db.Column(db.Text)
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    
    docentes = db.relationship('Docente', back_populates='colegio', lazy=True)
    alumnos = db.relationship('Alumno', back_populates='colegio', lazy=True)
    aulas = db.relationship('Aula', back_populates='colegio', lazy=True)
    asignaturas = db.relationship('Asignatura', back_populates='colegio', lazy=True)

    def __init__(self, nombre_colegio, codigo_dane=None, direccion=None, telefono=None, email=None):
        self.nombre_colegio = nombre_colegio
        self.codigo_dane = codigo_dane
        self.direccion = direccion
        self.telefono = telefono
        self.email = email

    def __repr__(self):
        return f"<Colegio '{self.nombre_colegio}' (DANE: {self.codigo_dane})>"


class Persona(db.Model):
    __tablename__ = 'persona'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    dni = db.Column(db.String(15), unique=True, nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    direccion = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100), unique=True)
    genero = db.Column(db.String(20))
    
    tipo_persona = db.Column(db.String(20))

    __mapper_args__ = {
        'polymorphic_on': tipo_persona,
        'polymorphic_identity': 'persona'
    }

    def __init__(self, nombre, apellido, dni, fecha_nacimiento, direccion=None, telefono=None, email=None, genero=None):
        self.nombre = nombre
        self.apellido = apellido
        self.dni = dni
        self.fecha_nacimiento = fecha_nacimiento
        self.direccion = direccion
        self.telefono = telefono
        self.email = email
        self.genero = genero

    def __repr__(self):
        return f"<Persona '{self.nombre} {self.apellido}' - DNI: {self.dni}>"


class Tutor(Persona):
    __tablename__ = 'tutor'
    
    id = db.Column(db.Integer, db.ForeignKey('persona.id'), primary_key=True)
    parentesco = db.Column(db.String(50))  
    ocupacion = db.Column(db.String(100))
    legal = db.Column(db.Boolean, nullable=False)

    alumnos_asociados = db.relationship('Alumno', secondary=alumno_tutor, back_populates='tutores', lazy='dynamic')

    __mapper_args__ = {
        'polymorphic_identity': 'tutor',
    }

    # El constructor llama a super() para rellenar los datos de Persona
    def __init__(self, nombre, apellido, dni, fecha_nacimiento, legal, parentesco=None, ocupacion=None, **kwargs):
        super().__init__(nombre=nombre, apellido=apellido, dni=dni, fecha_nacimiento=fecha_nacimiento, **kwargs)
        self.legal = legal
        self.parentesco = parentesco
        self.ocupacion = ocupacion

    def __repr__(self):
        return f"<Tutor '{self.nombre} {self.apellido}' - Parentesco: {self.parentesco}>"


class Docente(Persona):
    __tablename__ = 'docente'
    
    id = db.Column(db.Integer, db.ForeignKey('persona.id'), primary_key=True)
    id_colegio = db.Column(db.Integer, db.ForeignKey('colegio.id_colegio'), nullable=False)
    cuil = db.Column(db.String(20), unique=True, nullable=False)
    cargo = db.Column(db.String(50)) 
    fecha_contratacion = db.Column(db.Date, nullable=True)
    estado_contractual = db.Column(db.String(20), nullable=True)

    colegio = db.relationship('Colegio', back_populates='docentes')

    __mapper_args__ = {
        'polymorphic_identity': 'docente',
    }

    def __init__(self, nombre, apellido, dni, fecha_nacimiento, id_colegio, cuil, cargo=None, fecha_contratacion=None, estado_contractual=None, **kwargs):
        super().__init__(nombre=nombre, apellido=apellido, dni=dni, fecha_nacimiento=fecha_nacimiento, **kwargs)
        self.id_colegio = id_colegio
        self.cuil = cuil
        self.cargo = cargo
        self.fecha_contratacion = fecha_contratacion
        self.estado_contractual = estado_contractual

    def __repr__(self):
        return f"<Docente '{self.nombre} {self.apellido}' - CUIL: {self.cuil}>"


class Alumno(Persona):
    __tablename__ = 'alumno'
    
    id = db.Column(db.Integer, db.ForeignKey('persona.id'), primary_key=True)
    id_colegio = db.Column(db.Integer, db.ForeignKey('colegio.id_colegio'), nullable=False)
    cuil = db.Column(db.String(20), nullable=False) 
    legajo = db.Column(db.String(20), unique=True, nullable=False)
    
    tutores = db.relationship('Tutor', secondary=alumno_tutor, back_populates='alumnos_asociados', lazy='subquery')
    colegio = db.relationship('Colegio', back_populates='alumnos')

    __mapper_args__ = {
        'polymorphic_identity': 'alumno',
    }

    def __init__(self, nombre, apellido, dni, fecha_nacimiento, id_colegio, cuil, legajo, **kwargs):
        super().__init__(nombre=nombre, apellido=apellido, dni=dni, fecha_nacimiento=fecha_nacimiento, **kwargs)
        self.id_colegio = id_colegio
        self.cuil = cuil
        self.legajo = legajo

    def __repr__(self):
        return f"<Alumno '{self.nombre} {self.apellido}' - Legajo: {self.legajo}>"


class Asignatura(db.Model):
    __tablename__ = 'asignatura'
    id_asignatura = db.Column(db.Integer, primary_key=True)
    id_colegio = db.Column(db.Integer, db.ForeignKey('colegio.id_colegio'), nullable=False)
    nombre_asignatura = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    creditos = db.Column(db.Integer)

    colegio = db.relationship('Colegio', back_populates='asignaturas')

    def __init__(self, id_colegio, nombre_asignatura, descripcion=None, creditos=None):
        self.id_colegio = id_colegio
        self.nombre_asignatura = nombre_asignatura
        self.descripcion = descripcion
        self.creditos = creditos

    def __repr__(self):
        return f"<Asignatura '{self.nombre_asignatura}' - Créditos: {self.creditos}>"


class Aula(db.Model):
    __tablename__ = 'aula'
    id_aula = db.Column(db.Integer, primary_key=True)
    id_colegio = db.Column(db.Integer, db.ForeignKey('colegio.id_colegio'), nullable=False)
    nombre_aula = db.Column(db.String(50), nullable=False)
    capacidad = db.Column(db.Integer)
    ubicacion = db.Column(db.String(100))

    colegio = db.relationship('Colegio', back_populates='aulas')

    def __init__(self, id_colegio, nombre_aula, capacidad=None, ubicacion=None):
        self.id_colegio = id_colegio
        self.nombre_aula = nombre_aula
        self.capacidad = capacidad
        self.ubicacion = ubicacion

    def __repr__(self):
        return f"<Aula '{self.nombre_aula}' - Capacidad: {self.capacidad}>"


class Turno(db.Model):
    __tablename__ = 'turno'
    id_turno = db.Column(db.Integer, primary_key=True)
    nombre_turno = db.Column(db.String(50), nullable=False) # Mañana, Tarde, Noche
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)

    def __init__(self, nombre_turno, hora_inicio, hora_fin):
        self.nombre_turno = nombre_turno
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin

    def __repr__(self):
        return f"<Turno '{self.nombre_turno}' ({self.hora_inicio} - {self.hora_fin})>" """


# ==========================================
# 1. TABLAS INTERMEDIAS Y ASOCIATIVAS
# ==========================================

# Muchos a Muchos: Alumno <-> Tutor
alumno_tutor = db.Table('alumno_tutor',
    db.Column('alumno_id', db.Integer, db.ForeignKey('alumno.id', ondelete='CASCADE'), primary_key=True),
    db.Column('tutor_id', db.Integer, db.ForeignKey('tutor.id', ondelete='CASCADE'), primary_key=True)
)

# ==========================================
# 2. MODELOS BASE E INSTITUCIONALES
# ==========================================

class Colegio(db.Model):
    __tablename__ = 'colegio'
    id_colegio = db.Column(db.Integer, primary_key=True)
    nombre_colegio = db.Column(db.String(150), nullable=False)
    codigo_dane = db.Column(db.String(50), unique=True)
    direccion = db.Column(db.Text)
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    
    docentes = db.relationship('Docente', back_populates='colegio', lazy=True)
    alumnos = db.relationship('Alumno', back_populates='colegio', lazy=True)
    aulas = db.relationship('Aula', back_populates='colegio', lazy=True)
    asignaturas = db.relationship('Asignatura', back_populates='colegio', lazy=True)
    matriculas = db.relationship('Matricula', back_populates='colegio', lazy=True)

    def __init__(self, nombre_colegio, codigo_dane=None, direccion=None, telefono=None, email=None):
        self.nombre_colegio = nombre_colegio
        self.codigo_dane = codigo_dane
        self.direccion = direccion
        self.telefono = telefono
        self.email = email

    def __repr__(self):
        return f"<Colegio '{self.nombre_colegio}' (DANE: {self.codigo_dane})>"


class Aula(db.Model):
    __tablename__ = 'aula'
    id_aula = db.Column(db.Integer, primary_key=True)
    id_colegio = db.Column(db.Integer, db.ForeignKey('colegio.id_colegio'), nullable=False)
    nombre_aula = db.Column(db.String(50), nullable=False)
    capacidad = db.Column(db.Integer)
    ubicacion = db.Column(db.String(100))

    colegio = db.relationship('Colegio', back_populates='aulas')
    clases = db.relationship('Clase', back_populates='aula', lazy=True)

    def __init__(self, id_colegio, nombre_aula, capacidad=None, ubicacion=None):
        self.id_colegio = id_colegio
        self.nombre_aula = nombre_aula
        self.capacidad = capacidad
        self.ubicacion = ubicacion

    def __repr__(self):
        return f"<Aula '{self.nombre_aula}' - Capacidad: {self.capacidad}>"


class Turno(db.Model):
    __tablename__ = 'turno'
    id_turno = db.Column(db.Integer, primary_key=True)
    nombre_turno = db.Column(db.String(50), nullable=False) # Mañana, Tarde, Noche
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)

    clases = db.relationship('Clase', back_populates='turno', lazy=True)

    def __init__(self, nombre_turno, hora_inicio, hora_fin):
        self.nombre_turno = nombre_turno
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin

    def __repr__(self):
        return f"<Turno '{self.nombre_turno}' ({self.hora_inicio} - {self.hora_fin})>"


class Asignatura(db.Model):
    __tablename__ = 'asignatura'
    id_asignatura = db.Column(db.Integer, primary_key=True)
    id_colegio = db.Column(db.Integer, db.ForeignKey('colegio.id_colegio'), nullable=False)
    nombre_asignatura = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    creditos = db.Column(db.Integer)

    colegio = db.relationship('Colegio', back_populates='asignaturas')
    clases = db.relationship('Clase', back_populates='asignatura', lazy=True)

    def __init__(self, id_colegio, nombre_asignatura, descripcion=None, creditos=None):
        self.id_colegio = id_colegio
        self.nombre_asignatura = nombre_asignatura
        self.descripcion = descripcion
        self.creditos = creditos

    def __repr__(self):
        return f"<Asignatura '{self.nombre_asignatura}' - Créditos: {self.creditos}>"

# ==========================================
# 3. POLIMORFISMO (PERSONAS)
# ==========================================

class Persona(db.Model):
    __tablename__ = 'persona'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    dni = db.Column(db.String(15), unique=True, nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    direccion = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), unique=True)
    genero = db.Column(db.String(20), nullable=False)
    tipo_persona = db.Column(db.String(20)) # Discriminador

    __mapper_args__ = {
        'polymorphic_on': tipo_persona,
        'polymorphic_identity': 'persona'
    }

    def __repr__(self):
        return f"<{self.__class__.__name__} '{self.nombre} {self.apellido}' - DNI: {self.dni}>"


class Tutor(Persona):
    __tablename__ = 'tutor'
    id = db.Column(db.Integer, db.ForeignKey('persona.id'), primary_key=True)
    parentesco = db.Column(db.String(50))  
    ocupacion = db.Column(db.String(100))
    legal = db.Column(db.Boolean, nullable=False, default=False)

    # Corregido: Se unificó el comportamiento lazy eliminando 'dynamic'
    alumnos_asociados = db.relationship(
        'Alumno', 
        secondary=alumno_tutor, 
        back_populates='tutores'
    )

    __mapper_args__ = { 'polymorphic_identity': 'tutor' }


class Docente(Persona):
    __tablename__ = 'docente'
    id = db.Column(db.Integer, db.ForeignKey('persona.id'), primary_key=True)
    id_colegio = db.Column(db.Integer, db.ForeignKey('colegio.id_colegio'), nullable=False)
    cuil = db.Column(db.String(20), unique=True, nullable=False) # Consistente
    cargo = db.Column(db.String(50)) 
    fecha_contratacion = db.Column(db.Date, nullable=True)
    estado_contractual = db.Column(db.String(20), nullable=True)

    colegio = db.relationship('Colegio', back_populates='docentes')
    clases = db.relationship('Clase', back_populates='docente', lazy=True)

    __mapper_args__ = { 'polymorphic_identity': 'docente' }


class Alumno(Persona):
    __tablename__ = 'alumno'
    id = db.Column(db.Integer, db.ForeignKey('persona.id'), primary_key=True)
    id_colegio = db.Column(db.Integer, db.ForeignKey('colegio.id_colegio'), nullable=False)
    cuil = db.Column(db.String(20), unique=True, nullable=False) # Agregado unique=True por consistencia
    legajo = db.Column(db.String(20), unique=True, nullable=False)
    
    # Corregido: Mismo comportamiento de relación que Tutor
    tutores = db.relationship(
        'Tutor', 
        secondary=alumno_tutor, 
        back_populates='alumnos_asociados'
    )
    colegio = db.relationship('Colegio', back_populates='alumnos')
    matriculas = db.relationship('Matricula', back_populates='alumno', lazy=True)
    asistencias = db.relationship('Asistencia', back_populates='alumno', lazy=True)

    __mapper_args__ = { 'polymorphic_identity': 'alumno' }

""" class Persona(db.Model):

    __tablename__ = 'persona'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    dni = db.Column(db.String(15), unique=True, nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    direccion = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), unique=True)
    genero = db.Column(db.String(20), nullable=False)
    tipo_persona = db.Column(db.String(20))

    __mapper_args__ = {
        'polymorphic_on': tipo_persona,
        'polymorphic_identity': 'persona'
    }

    def __init__(self, nombre, apellido, dni, fecha_nacimiento, direccion, telefono, email, genero):
        self.nombre = nombre
        self.apellido = apellido
        self.dni = dni
        self.fecha_nacimiento = fecha_nacimiento
        self.direccion = direccion
        self.telefono = telefono
        self.email = email
        self.genero = genero

    def __repr__(self):
        return f"<Persona '{self.nombre} {self.apellido}' - DNI: {self.dni}>"


class Tutor(Persona):
    __tablename__ = 'tutor'
    id = db.Column(db.Integer, db.ForeignKey('persona.id'), primary_key=True)
    parentesco = db.Column(db.String(50))  
    ocupacion = db.Column(db.String(100))
    legal = db.Column(db.Boolean, nullable=False)

    alumnos_asociados = db.relationship('Alumno', secondary=alumno_tutor, back_populates='tutores', lazy='dynamic')

    __mapper_args__ = { 'polymorphic_identity': 'tutor' }

    def __init__(self, nombre, apellido, dni, fecha_nacimiento, legal, parentesco=None, ocupacion=None, direccion=None, telefono=None, email=None, genero=None):
        super().__init__(nombre=nombre, apellido=apellido, dni=dni, fecha_nacimiento=fecha_nacimiento, direccion=direccion, telefono=telefono, email=email, genero=genero)
        self.legal = legal
        self.parentesco = parentesco
        self.ocupacion = ocupacion

    def __repr__(self):
        return f"<Tutor '{self.nombre} {self.apellido}' - Parentesco: {self.parentesco}>"


class Docente(Persona):
    __tablename__ = 'docente'
    id = db.Column(db.Integer, db.ForeignKey('persona.id'), primary_key=True)
    id_colegio = db.Column(db.Integer, db.ForeignKey('colegio.id_colegio'), nullable=False)
    cuil = db.Column(db.String(20), unique=True, nullable=False)
    cargo = db.Column(db.String(50)) 
    fecha_contratacion = db.Column(db.Date, nullable=True)
    estado_contractual = db.Column(db.String(20), nullable=True)

    colegio = db.relationship('Colegio', back_populates='docentes')
    clases = db.relationship('Clase', back_populates='docente', lazy=True)

    __mapper_args__ = { 'polymorphic_identity': 'docente' }

    def __init__(self, nombre, apellido, dni, fecha_nacimiento, id_colegio, direccion, telefono, email, genero=None, cargo=None, fecha_contratacion=None, estado_contractual=None):
        super().__init__(nombre=nombre, apellido=apellido, dni=dni, fecha_nacimiento=fecha_nacimiento, direccion=direccion, telefono=telefono, email=email, genero=genero)
        self.id_colegio = id_colegio
        self.cuil = cuil
        self.cargo = cargo
        self.fecha_contratacion = fecha_contratacion
        self.estado_contractual = estado_contractual

    def __repr__(self):
        return f"<Docente '{self.nombre} {self.apellido}' - CUIL: {self.cuil}>"


class Alumno(Persona):
    __tablename__ = 'alumno'
    id = db.Column(db.Integer, db.ForeignKey('persona.id'), primary_key=True)
    id_colegio = db.Column(db.Integer, db.ForeignKey('colegio.id_colegio'), nullable=False)
    cuil = db.Column(db.String(20), nullable=False) 
    legajo = db.Column(db.String(20), unique=True, nullable=False)
    
    tutores = db.relationship('Tutor', secondary=alumno_tutor, back_populates='alumnos_asociados', lazy='subquery')
    colegio = db.relationship('Colegio', back_populates='alumnos')
    matriculas = db.relationship('Matricula', back_populates='alumno', lazy=True)
    asistencias = db.relationship('Asistencia', back_populates='alumno', lazy=True)

    __mapper_args__ = { 'polymorphic_identity': 'alumno' }

    def __init__(self, nombre, apellido, dni, fecha_nacimiento, id_colegio, cuil, legajo, **kwargs):
        super().__init__(nombre=nombre, apellido=apellido, dni=dni, fecha_nacimiento=fecha_nacimiento, direccion=direccion, telefono=telefono, email=email, genero=genero)
        self.id_colegio = id_colegio
        self.cuil = cuil
        self.legajo = legajo

    def __repr__(self):
        return f"<Alumno '{self.nombre} {self.apellido}' - Legajo: {self.legajo}>" """

# ==========================================
# 4. NUEVOS MODELOS (GESTIÓN ACADÉMICA)
# ==========================================

class Clase(db.Model):
    """Representa la sección o grupo específico (Ej: Matemática de 5to Año, Aula 3, Turno Mañana)."""
    __tablename__ = 'clase'
    id_clase = db.Column(db.Integer, primary_key=True)
    id_asignatura = db.Column(db.Integer, db.ForeignKey('asignatura.id_asignatura'), nullable=False)
    id_docente = db.Column(db.Integer, db.ForeignKey('docente.id'), nullable=False)
    id_aula = db.Column(db.Integer, db.ForeignKey('aula.id_aula'), nullable=False)
    id_turno = db.Column(db.Integer, db.ForeignKey('turno.id_turno'), nullable=False)
    ciclo_lectivo = db.Column(db.Integer, nullable=False) # Ej: 2026

    asignatura = db.relationship('Asignatura', back_populates='clases')
    docente = db.relationship('Docente', back_populates='clases')
    aula = db.relationship('Aula', back_populates='clases')
    turno = db.relationship('Turno', back_populates='clases')
    horarios = db.relationship('Horario', back_populates='clase', lazy=True, cascade="all, delete-orphan")
    asistencias = db.relationship('Asistencia', back_populates='clase', lazy=True)

    def __init__(self, id_asignatura, id_docente, id_aula, id_turno, ciclo_lectivo):
        self.id_asignatura = id_asignatura
        self.id_docente = id_docente
        self.id_aula = id_aula
        self.id_turno = id_turno
        self.ciclo_lectivo = ciclo_lectivo
    
    def repr(self):return f"<Clase ID: {self.id_clase} - Asignatura: {self.id_asignatura} - Año: {self.ciclo_lectivo}>"

class Horario(db.Model):
    """Define los días de la semana y las horas específicas en las que se dicta una Clase."""
    __tablename__ = 'horario'
    id_horario = db.Column(db.Integer, primary_key=True)
    id_clase = db.Column(db.Integer, db.ForeignKey('clase.id_clase', ondelete='CASCADE'), nullable=False)
    dia_semana = db.Column(db.String(15), nullable=False) # Lunes, Martes, etc.
    hora_desde = db.Column(db.Time, nullable=False)
    hora_hasta = db.Column(db.Time, nullable=False)

    clase = db.relationship('Clase', back_populates='horarios')

    def init(self, id_clase, dia_semana, hora_desde, hora_hasta):
        self.id_clase = id_clase
        self.dia_semana = dia_semana
        self.hora_desde = hora_desde
        self.hora_hasta = hora_hasta

    def repr(self):return f"<Horario {self.dia_semana} {self.hora_desde} - {self.hora_hasta}>"

class Matricula(db.Model):
    """Vincula a un alumno con una institución y un año escolar determinado."""
    __tablename__ = 'matricula'
    id_matricula = db.Column(db.Integer, primary_key=True)
    id_alumno = db.Column(db.Integer, db.ForeignKey('alumno.id'), nullable=False)
    id_colegio = db.Column(db.Integer, db.ForeignKey('colegio.id_colegio'), nullable=False)
    fecha_inscripcion = db.Column(db.Date, nullable=False)
    grado_nivel = db.Column(db.String(50), nullable=False) # Ej: 5to Año Secundaria
    periodo_lectivo = db.Column(db.Integer, nullable=False) # Ej: 2026
    estado_matricula = db.Column(db.String(20), default="Activo") # Activo, Baja, Suspendido
    alumno = db.relationship('Alumno', back_populates='matriculas')
    colegio = db.relationship('Colegio', back_populates='matriculas')
    def init(self, id_alumno, id_colegio, fecha_inscripcion, grado_nivel, periodo_lectivo, estado_matricula="Activo"):
        self.id_alumno = id_alumno
        self.id_colegio = id_colegio
        self.fecha_inscripcion = fecha_inscripcion
        self.grado_nivel = grado_nivel
        self.periodo_lectivo = periodo_lectivo
        self.estado_matricula = estado_matricula
        
    def repr(self):
        return f"<Matricula Alumno ID: {self.id_alumno} - Grado: {self.grado_nivel} ({self.periodo_lectivo})>"

class Asistencia(db.Model):
    """Registra el presentismo diario de un alumno en una determinada Clase."""
    __tablename__ = 'asistencia'
    id_asistencia = db.Column(db.Integer, primary_key=True)
    id_alumno = db.Column(db.Integer, db.ForeignKey('alumno.id'), nullable=False)
    id_clase = db.Column(db.Integer, db.ForeignKey('clase.id_clase'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    estado_asistencia = db.Column(db.String(20), nullable=False) # Presente, Ausente, Tarde, Justificado
    observaciones = db.Column(db.String(255))
    alumno = db.relationship('Alumno', back_populates='asistencias')

    clase = db.relationship('Clase', back_populates='asistencias')
    def init(self, id_alumno, id_clase, fecha, estado_asistencia, observaciones=None):
        self.id_alumno = id_alumno
        self.id_clase = id_clase
        self.fecha = fecha
        self.estado_asistencia = estado_asistencia
        self.observaciones = observaciones
        def repr(self):
            return f"<Asistencia Alumno ID: {self.id_alumno} - Fecha: {self.fecha} - Estado: {self.estado_asistencia}>"