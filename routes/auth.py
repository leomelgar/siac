from flask import Blueprint, request, redirect, url_for, render_template, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from utils.db import db
from models.colege import Usuario, Persona, Rol

auth = Blueprint('auth', __name__, url_prefix='/auth')


# ======================================================
# LOGIN / LOGOUT
# ======================================================

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('alumnos.home'))  # ajustá al endpoint que uses como "inicio"

    if request.method == 'GET':
        return render_template('auth/login.html')

    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        flash('Usuario y contraseña son obligatorios', 'warning')
        return redirect(url_for('auth.login'))

    usuario = Usuario.query.filter_by(username=username).first()

    if usuario is None or not check_password_hash(usuario.password_hash, password):
        flash('Credenciales inválidas', 'danger')
        return redirect(url_for('auth.login'))

    if not usuario.activo:
        flash('Usuario deshabilitado', 'danger')
        return redirect(url_for('auth.login'))

    login_user(usuario, remember=bool(request.form.get('remember')))
    flash(f'Bienvenido, {usuario.username}', 'success')
    return redirect(url_for('alumnos.home'))  # ajustá al endpoint que uses como "inicio"


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('auth.login'))


# ======================================================
# REGISTRAR (asignar usuario/contraseña a una Persona existente)
# ======================================================

@auth.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'GET':
        id_persona = request.args.get('id_persona')
        persona = Persona.query.get(id_persona) if id_persona else None

        # Si la persona ya tiene usuario, no tiene sentido mostrar el formulario
        if persona is not None and persona.usuario is not None:
            flash('Esta persona ya tiene un usuario asignado', 'warning')
            return redirect(request.referrer or url_for('auth.login'))

        roles = Rol.query.all()
        return render_template('auth/registrar.html', persona=persona, roles=roles)

    return _registrar_post()


def _registrar_post():
    """
    Crea un Usuario asociado a una Persona ya existente (Alumno, Docente o Tutor).
    Asume que la Persona y el Rol ya fueron creados previamente.
    """
    id_persona = request.form.get('id_persona')
    id_rol = request.form.get('id_rol')
    username = request.form.get('username')
    password = request.form.get('password')

    if not all([id_persona, id_rol, username, password]):
        flash('Faltan campos obligatorios', 'warning')
        return redirect(url_for('auth.registrar', id_persona=id_persona))

    persona = Persona.query.get(id_persona)
    if persona is None:
        flash('La persona indicada no existe', 'danger')
        return redirect(url_for('auth.registrar'))

    if persona.usuario is not None:
        flash('Esta persona ya tiene un usuario asignado', 'warning')
        return redirect(url_for('auth.registrar'))

    if Usuario.query.filter_by(username=username).first():
        flash('El username ya está en uso, elegí otro', 'danger')
        return redirect(url_for('auth.registrar', id_persona=id_persona))

    try:
        nuevo_usuario = Usuario(
            id_persona=id_persona,
            id_rol=id_rol,
            username=username,
            password_hash=generate_password_hash(password)
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear el usuario: {e}', 'danger')
        return redirect(url_for('auth.registrar', id_persona=id_persona))

    flash(f'Usuario "{username}" creado correctamente para {persona.nombre} {persona.apellido}', 'success')
    return redirect(url_for('auth.login'))


# ======================================================
# PERFIL DEL USUARIO ACTUAL
# ======================================================

@auth.route('/me')
@login_required
def me():
    return render_template('auth/me.html', usuario=current_user, persona=current_user.persona)