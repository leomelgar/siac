from flask import render_template


def register_error_handlers(app):
    """Se llama una vez desde create_app() para registrar páginas de error propias."""

    @app.errorhandler(401)
    def no_autenticado(error):
        return render_template('errores/401.html'), 401

    @app.errorhandler(403)
    def sin_permiso(error):
        return render_template('errores/403.html'), 403

    @app.errorhandler(404)
    def no_encontrado(error):
        return render_template('errores/404.html'), 404