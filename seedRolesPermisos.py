"""
Script de inicialización de Roles y Permisos.
Correr una sola vez (o cada vez que agregues un permiso nuevo):

    python seed_roles_permisos.py
"""
from app import create_app
from utils.db import db
from models.colege import Rol, Permiso

app = create_app()

# Catálogo de permisos del sistema (agregá acá los que necesites)
PERMISOS = [
    ('CARGAR_DOCENTE', 'Crear, editar y borrar docentes'),
    ('CARGAR_ALUMNO', 'Crear, editar y borrar alumnos'),
    ('CARGAR_NOTAS', 'Cargar calificaciones'),
    ('CERRAR_NOTAS', 'Cerrar calificaciones de un trimestre'),
    ('VER_NOTAS', 'Ver calificaciones'),
    ('CARGAR_ASISTENCIA', 'Registrar asistencia diaria'),
    ('GESTION_CLASES', 'Crear, editar y borrar clases'),
]

# Qué permisos tiene cada rol
ROLES = {
    'DIRECTIVO': ['CARGAR_DOCENTE', 'CARGAR_ALUMNO', 'CARGAR_NOTAS', 'CERRAR_NOTAS', 'VER_NOTAS', 'CARGAR_ASISTENCIA', 'GESTION_CLASES'],
    'PRECEPTOR': ['CARGAR_ASISTENCIA', 'VER_NOTAS', 'CARGAR_NOTAS', 'GESTION_CLASES', 'CERRAR_NOTAS'],
    'DOCENTE':   ['CARGAR_NOTAS', 'VER_NOTAS'],
}

with app.app_context():
    # 1. Crear permisos que no existan todavía
    permisos_map = {}
    for nombre, descripcion in PERMISOS:
        permiso = Permiso.query.filter_by(nombre_permiso=nombre).first()
        if permiso is None:
            permiso = Permiso(nombre_permiso=nombre, descripcion=descripcion)
            db.session.add(permiso)
        permisos_map[nombre] = permiso

    db.session.commit()

    # 2. Crear roles y asignarles sus permisos
    for nombre_rol, nombres_permisos in ROLES.items():
        rol = Rol.query.filter_by(nombre_rol=nombre_rol).first()
        if rol is None:
            rol = Rol(nombre_rol=nombre_rol)
            db.session.add(rol)
            db.session.flush()  # para poder usar rol.permisos antes del commit

        for nombre_permiso in nombres_permisos:
            permiso = permisos_map[nombre_permiso]
            if permiso not in rol.permisos:
                rol.permisos.append(permiso)

    db.session.commit()
    print("Roles y permisos inicializados correctamente.")