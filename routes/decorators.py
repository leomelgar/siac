from functools import wraps
from flask import abort
from flask_login import current_user


def permiso_requerido(nombre_permiso):
    """
    Decorador para proteger rutas según el permiso asignado al Rol del usuario.
    Uso:
        @app.route('/cargar-notas')
        @login_required
        @permiso_requerido('CARGAR_NOTAS')
        def cargar_notas():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)

            permisos_rol = {p.nombre_permiso for p in current_user.rol.permisos}

            if nombre_permiso not in permisos_rol:
                abort(403)

            return f(*args, **kwargs)
        return decorated
    return decorator