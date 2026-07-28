def tiene_permiso(usuario, nombre_permiso):
    """
    Filtro Jinja: {{ current_user|tiene_permiso('CARGAR_DOCENTE') }}

    Devuelve True si el usuario está logueado y su Rol tiene ese permiso asignado.
    Si el usuario es anónimo (no logueado), devuelve False directamente
    sin tocar `.rol` (evitaría un error, ya que AnonymousUserMixin no lo tiene).
    """
    if not getattr(usuario, 'is_authenticated', False):
        return False

    return any(p.nombre_permiso == nombre_permiso for p in usuario.rol.permisos)


def register_filters(app):
    """Se llama una vez desde create_app() para registrar todos los filtros custom."""
    app.jinja_env.filters['tiene_permiso'] = tiene_permiso