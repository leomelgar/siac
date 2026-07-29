from utils.db import db
from datetime import datetime
from flask_login import UserMixin
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
    # NUEVO MÉTODO: Convierte la instancia en un diccionario
    def to_dict(self):
        return {
            "id_asignatura": self.id_asignatura,
            "id_colegio": self.id_colegio,
            "nombre_asignatura": self.nombre_asignatura,
            "descripcion": self.descripcion,
            "creditos": self.creditos
        }

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
    telefono = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    genero = db.Column(db.String(20), nullable=False)
    tipo_persona = db.Column(db.String(20)) # Discriminador

    __mapper_args__ = {
        'polymorphic_on': tipo_persona,
        'polymorphic_identity': 'persona'
    }

    def __repr__(self):
        return f"<{self.__class__.__name__} '{self.nombre} {self.apellido}' - DNI: {self.dni}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "dni": self.dni,
            # Las fechas no son serializables nativamente en JSON, usamos isoformat()
            "fecha_nacimiento": self.fecha_nacimiento.isoformat() if self.fecha_nacimiento else None,
            "direccion": self.direccion,
            "telefono": self.telefono,
            "email": self.email,
            "genero": self.genero,
            "tipo_persona": self.tipo_persona
        }


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

    def to_dict(self):
        # Heredamos los datos base y agregamos los específicos
        data = super().to_dict()
        data.update({
            "parentesco": self.parentesco,
            "ocupacion": self.ocupacion,
            "legal": self.legal
        })
        return data

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

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "id_colegio": self.id_colegio,
            "cuil": self.cuil,
            "cargo": self.cargo,
            "fecha_contratacion": self.fecha_contratacion.isoformat() if self.fecha_contratacion else None,
            "estado_contractual": self.estado_contractual
        })
        return data

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

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "id_colegio": self.id_colegio,
            "cuil": self.cuil,
            "legajo": self.legajo
        })
        return data

# Tabla asociativa Muchos a Muchos: Rol <-> Permiso
rol_permiso = db.Table('rol_permiso',
    db.Column('id_rol', db.Integer, db.ForeignKey('rol.id_rol', ondelete='CASCADE'), primary_key=True),
    db.Column('id_permiso', db.Integer, db.ForeignKey('permiso.id_permiso', ondelete='CASCADE'), primary_key=True)
)

class Permiso(db.Model):
    __tablename__ = 'permiso'
    id_permiso = db.Column(db.Integer, primary_key=True)
    nombre_permiso = db.Column(db.String(50), unique=True, nullable=False) # Ej: "CARGAR_NOTAS", "VER_BOLETIN"
    descripcion = db.Column(db.String(150))

    def __init__(self, nombre_permiso, descripcion=None):
        self.nombre_permiso = nombre_permiso
        self.descripcion = descripcion

class Rol(db.Model):
    __tablename__ = 'rol'
    id_rol = db.Column(db.Integer, primary_key=True)
    nombre_rol = db.Column(db.String(50), unique=True, nullable=False) # Ej: "DIRECTIVO", "PRECEPTOR", "DOCENTE"
    
    permisos = db.relationship('Permiso', secondary=rol_permiso, backref=db.backref('roles', lazy='dynamic'))

    def __init__(self, nombre_rol):
        self.nombre_rol = nombre_rol

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuario'
    id_usuario = db.Column(db.Integer, primary_key=True)
    id_persona = db.Column(db.Integer, db.ForeignKey('persona.id'), unique=True, nullable=False)
    id_rol = db.Column(db.Integer, db.ForeignKey('rol.id_rol'), nullable=False)
 
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    activo = db.Column(db.Boolean, default=True)
 
    persona = db.relationship('Persona', backref=db.backref('usuario', uselist=False))
    rol = db.relationship('Rol', backref='usuarios')
 
    def __init__(self, id_persona, id_rol, username, password_hash, activo=True):
        self.id_persona = id_persona
        self.id_rol = id_rol
        self.username = username
        self.password_hash = password_hash
        self.activo = activo
 
    # --- Requerido por Flask-Login ---
    def get_id(self):
        return str(self.id_usuario)
 
    # UserMixin ya provee por defecto:
    #   is_authenticated -> True
    #   is_anonymous     -> False
    # Pero is_active lo sobreescribimos para que respete tu columna 'activo'
    @property
    def is_active(self):
        return self.activo

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

class Calificacion(db.Model):
    __tablename__ = 'calificacion'
    id_calificacion = db.Column(db.Integer, primary_key=True)
    id_alumno = db.Column(db.Integer, db.ForeignKey('alumno.id'), nullable=False)
    id_clase = db.Column(db.Integer, db.ForeignKey('clase.id_clase'), nullable=False)
    
    # Instancia: 1er Trimestre, 2do Trimestre, Mesa Diciembre, Mesa Febrero/Marzo
    instancia = db.Column(db.String(50), nullable=False) 
    
    # Se usa String por si la calificación es conceptual (TEA, TEP, TED) o numérica
    valor = db.Column(db.String(10), nullable=False) 
    fecha_carga = db.Column(db.DateTime, default=datetime.utcnow)
    observaciones = db.Column(db.String(255))

    alumno = db.relationship('Alumno', backref='calificaciones')
    clase = db.relationship('Clase', backref='calificaciones')

    def __init__(self, id_alumno, id_clase, instancia, valor, observaciones=None):
        self.id_alumno = id_alumno
        self.id_clase = id_clase
        self.instancia = instancia
        self.valor = valor
        self.observaciones = observaciones

"""Boletín de Calificaciones (El documento consolidado)
Aunque se podrían calcular los promedios al vuelo leyendo la tabla Calificacion, 
en el sistema educativo argentino el Boletín (y posteriormente el Libro Matriz) 
es un documento oficial que debe quedar "congelado" al cerrar el año escolar. 
Por eso, conviene tener una estructura Boletin (cabecera) y DetalleBoletin (una fila por materia).
Preceptores y Roles dinámicos: Al tener una tabla Rol con Permisos, podés crear el rol de Preceptor
 y asignarle el permiso CARGAR_ASISTENCIA y VER_NOTAS, pero no CARGAR_NOTAS. Si un directivo necesita 
 cargar una nota excepcionalmente, su rol sí se lo permitirá.

Historial vs Documento Oficial: Los profesores insertan registros en Calificacion durante el año. 
Al finalizar el trimestre, el Preceptor (o el sistema automáticamente) aprieta un botón que calcula 
el promedio y hace un UPDATE sobre DetalleBoletin. Esto asegura que el boletín pueda ser impreso rápidamente
 sin procesar miles de notas al vuelo.

Manejo de Medias Faltas: En DetalleBoletin definí total_faltas como Numeric(4, 1) 
porque en Argentina el sistema de ausencias (llegadas tarde) computa como "media falta" (0.5). """
class Boletin(db.Model):
    """Cabecera del documento oficial generado por la matrícula anual de un alumno."""
    __tablename__ = 'boletin'
    id_boletin = db.Column(db.Integer, primary_key=True)
    id_matricula = db.Column(db.Integer, db.ForeignKey('matricula.id_matricula'), unique=True, nullable=False)
    fecha_emision = db.Column(db.Date, nullable=True)
    estado_cierre = db.Column(db.Boolean, default=False) # True cuando el año lectivo terminó

    matricula = db.relationship('Matricula', backref=db.backref('boletin', uselist=False))
    detalles = db.relationship('DetalleBoletin', back_populates='boletin', cascade="all, delete-orphan")

    def __init__(self, id_matricula, fecha_emision=None):
        self.id_matricula = id_matricula
        self.fecha_emision = fecha_emision

class DetalleBoletin(db.Model):
    """Fila del boletín correspondiente a una asignatura específica."""
    __tablename__ = 'detalle_boletin'
    id_detalle = db.Column(db.Integer, primary_key=True)
    id_boletin = db.Column(db.Integer, db.ForeignKey('boletin.id_boletin'), nullable=False)
    id_asignatura = db.Column(db.Integer, db.ForeignKey('asignatura.id_asignatura'), nullable=False)
    
    # Notas por etapa
    nota_t1 = db.Column(db.String(10))
    nota_t2 = db.Column(db.String(10))
    nota_t3 = db.Column(db.String(10))
    promedio_anual = db.Column(db.Numeric(4, 2))
    
    # Mesas de examen
    nota_diciembre = db.Column(db.String(10))
    nota_marzo = db.Column(db.String(10))
    
    # Estado final: Aprobada, Previa, Equivalencia
    estado_materia = db.Column(db.String(30), default="Cursando") 
    
    # Resumen de faltas para esa materia específica (muy común en escuelas técnicas)
    total_faltas = db.Column(db.Numeric(4, 1), default=0) # Permite 0.5 (media falta)

    boletin = db.relationship('Boletin', back_populates='detalles')
    asignatura = db.relationship('Asignatura')

    def __init__(self, id_boletin, id_asignatura):
        self.id_boletin = id_boletin
        self.id_asignatura = id_asignatura

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

    # Constraint de unicidad
    __table_args__ = (
        db.UniqueConstraint(
            'id_alumno', 'id_colegio', 'periodo_lectivo',
            name='uq_matricula_alumno_colegio_periodo'
        ),
    )

# ==========================================
# ASISTENCIA DIARIA (Modificada)
# ==========================================
class Asistencia(db.Model):
    """Registra el presentismo diario, contemplando llegadas tarde y retiros anticipados."""
    __tablename__ = 'asistencia'
    id_asistencia = db.Column(db.Integer, primary_key=True)
    id_alumno = db.Column(db.Integer, db.ForeignKey('alumno.id'), nullable=False)
    id_clase = db.Column(db.Integer, db.ForeignKey('clase.id_clase'), nullable=False)
    fecha = db.Column(db.Date, nullable=False, default=datetime.today)
    
    # Valores típicos: "Presente", "Ausente", "Llegada Tarde", "Retiro Anticipado"
    tipo_registro = db.Column(db.String(30), nullable=False) 
    
    # Lógica Argentina: 1.0 (Ausencia completa), 0.5 (Media falta), 0.0 (Presente)
    # Usamos Numeric para manejar los decimales con precisión exacta en la BD
    valor_falta = db.Column(db.Numeric(3, 2), nullable=False, default=0.0)
    
    # Sistema de justificación
    justificada = db.Column(db.Boolean, default=False)
    motivo_justificacion = db.Column(db.String(150))
    fecha_justificacion = db.Column(db.Date, nullable=True) # Cuándo trajo el certificado
    
    alumno = db.relationship('Alumno', back_populates='asistencias')
    clase = db.relationship('Clase', back_populates='asistencias')

    def __init__(self, id_alumno, id_clase, fecha, tipo_registro, valor_falta=0.0):
        self.id_alumno = id_alumno
        self.id_clase = id_clase
        self.fecha = fecha
        self.tipo_registro = tipo_registro
        self.valor_falta = valor_falta

# ==========================================
# ESTADO DE REGULARIDAD (Totalizador)
# ==========================================
class EstadoRegularidad(db.Model):
    """
    Lleva el conteo global anual del alumno y su estado (Regular/Libre). 
    Evita tener que hacer un SUM() de todas las asistencias cada vez que se carga una falta.
    """
    __tablename__ = 'estado_regularidad'
    id_regularidad = db.Column(db.Integer, primary_key=True)
    id_matricula = db.Column(db.Integer, db.ForeignKey('matricula.id_matricula'), unique=True, nullable=False)
    
    # Contadores actualizados automáticamente (mediante triggers de BD o lógica en la app)
    total_faltas = db.Column(db.Numeric(5, 2), default=0.0)
    total_faltas_justificadas = db.Column(db.Numeric(5, 2), default=0.0)
    
    # Estados: "Regular", "Libre (15 faltas)", "Reincorporado", "Libre Definitivo"
    condicion = db.Column(db.String(50), default="Regular")
    
    # Límite dinámico: Empieza en 15.0, sube a 25.0 si se aprueba la 1ra reincorporación
    limite_actual = db.Column(db.Numeric(4, 2), default=15.0) 
    
    matricula = db.relationship('Matricula', backref=db.backref('estado_regularidad', uselist=False))

    def verificar_estado(self):
        """Método de ayuda para evaluar si el alumno quedó libre."""
        if self.total_faltas >= self.limite_actual:
            if self.limite_actual == 15.0:
                self.condicion = "Libre (15 faltas)"
            else:
                self.condicion = "Libre Definitivo"

# ==========================================
# TRÁMITE DE REINCORPORACIÓN
# ==========================================
class TramiteReincorporacion(db.Model):
    """
    Registro del pedido formal (Acta) iniciado por el Tutor legal
    para devolverle la regularidad a un alumno libre.
    """
    __tablename__ = 'tramite_reincorporacion'
    id_tramite = db.Column(db.Integer, primary_key=True)
    id_matricula = db.Column(db.Integer, db.ForeignKey('matricula.id_matricula'), nullable=False)
    id_tutor = db.Column(db.Integer, db.ForeignKey('tutor.id'), nullable=False) # Quién firma
    
    fecha_solicitud = db.Column(db.Date, nullable=False, default=datetime.today)
    
    # Instancia: "Primera (15 faltas)", "Segunda (25 faltas)"
    instancia = db.Column(db.String(50), nullable=False) 
    
    # Estados del trámite: "Pendiente", "Aprobado", "Rechazado"
    estado_tramite = db.Column(db.String(20), default="Pendiente")
    
    # Argumento del tutor y resolución oficial del colegio
    motivo_tutor = db.Column(db.Text, nullable=False)
    resolucion_directiva = db.Column(db.Text)
    fecha_resolucion = db.Column(db.Date)
    
    matricula = db.relationship('Matricula', backref='reincorporaciones')
    tutor = db.relationship('Tutor')

    def aprobar_tramite(self, resolucion):
        """Lógica para aprobar y extender el límite de faltas."""
        self.estado_tramite = "Aprobado"
        self.resolucion_directiva = resolucion
        self.fecha_resolucion = datetime.today()
        
        # Al aprobarse, se actualiza el EstadoRegularidad asociado a la matrícula
        if self.instancia == "Primera (15 faltas)":
            self.matricula.estado_regularidad.limite_actual = 25.0
            self.matricula.estado_regularidad.condicion = "Reincorporado"