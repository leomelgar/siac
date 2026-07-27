from flask import Blueprint, request, jsonify, redirect, url_for, render_template, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from utils.db import db
from models.colege import Usuario, Persona

auth = Blueprint('auth', __name__, url_prefix='/auth')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('alumnos.home'))  # ajustá al endpoint que uses como "inicio"

    if request.method == 'GET':
        return render_template('auth/login.html')  # crear templates/auth/login.html

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
    return redirect(url_for('alumnos.home'))  # ajustá al endpoint que uses como "inicio"


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/me', methods=['GET'])
@login_required
def me():
    """Devuelve los datos de la persona/usuario actualmente logueado."""
    persona = current_user.persona
    return jsonify({
        "username": current_user.username,
        "rol": current_user.rol.nombre_rol,
        "persona": persona.to_dict() if persona else None
    }), 200


@auth.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'GET':
        return render_template('auth/registrar.html')  # crear si necesitás UI para esto
    return _registrar_post()


def _registrar_post():
    """
    Crea un Usuario asociado a una Persona ya existente (Alumno, Docente o Tutor).
    Asume que la Persona y el Rol ya fueron creados previamente.
    """
    data = request.form or request.get_json(silent=True) or {}

    id_persona = data.get('id_persona')
    id_rol = data.get('id_rol')
    username = data.get('username')
    password = data.get('password')

    if not all([id_persona, id_rol, username, password]):
        flash('Faltan campos obligatorios', 'warning')
        return redirect(url_for('auth.registrar'))

    persona = Persona.query.get(id_persona)
    if persona is None:
        flash('La persona indicada no existe', 'danger')
        return redirect(url_for('auth.registrar'))

    if Usuario.query.filter_by(username=username).first():
        flash('El username ya está en uso', 'danger')
        return redirect(url_for('auth.registrar'))

    nuevo_usuario = Usuario(
        id_persona=id_persona,
        id_rol=id_rol,
        username=username,
        password_hash=generate_password_hash(password)
    )

    db.session.add(nuevo_usuario)
    db.session.commit()

    flash('Usuario creado correctamente', 'success')
    return redirect(url_for('auth.login'))