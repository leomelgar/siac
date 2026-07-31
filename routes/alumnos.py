from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models.colege import Alumno, Tutor, Persona, Colegio, alumno_tutor
from utils.db import db
from datetime import datetime as dt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

alumnos = Blueprint("alumnos", __name__)

@alumnos.before_request
@login_required
def requerir_login():
    pass

@alumnos.route('/alumnos/home', methods=["GET"]) #listado de alumnos
def home():
    # Capturamos el parámetro 'tag' de la URL.
    tag_busqueda = request.args.get('tag', '').strip()
    if tag_busqueda:
        # Buscar por apellido O por legajo ignorando mayúsculas/minúsculas (ilike)
        alumnos_db = Alumno.query.filter(
            (Alumno.apellido.ilike(f'%{tag_busqueda}%')) |
            (Alumno.legajo.ilike(f'%{tag_busqueda}%'))
        ).all()
    else:
        # Si no hay búsqueda (entro por primera vez), traemos todos
        alumnos_db = Alumno.query.all()

    lista_alumnos = []
    for a in alumnos_db:
        lista_alumnos.append({
            "id": a.id,
            "legajo": a.legajo,
            "apellido": a.apellido,
            "nombre": a.nombre,
            "cuil": a.cuil
        })
    cantidad = len(lista_alumnos)
    return render_template('/alumnos/home.html',
                           alumnos=lista_alumnos,
                           cantidad=cantidad)


@alumnos.route('/inscripcion')
def inscripcion():
    return render_template('/alumnos/new.html')


# --- FUNCIÓN GENERADORA DE LEGAJO ---
def generar_nuevo_legajo():
    """Genera un legajo con el formato AAAA-NNNN (Ej: 2026-0001)"""
    año_actual = dt.now().year
    prefijo = f"{año_actual}-"

    ultimo_alumno = Alumno.query.filter(
        Alumno.legajo.like(f"{prefijo}%")
    ).order_by(Alumno.legajo.desc()).first()

    if ultimo_alumno:
        ultimo_numero = int(ultimo_alumno.legajo.split('-')[1])
        nuevo_numero = ultimo_numero + 1
    else:
        nuevo_numero = 1

    return f"{prefijo}{nuevo_numero:04d}"


@alumnos.route('/newAlumno', methods=['POST'])
def new_alumno():
    colegio = Colegio.query.first()

    try:
        # 1. Fecha del alumno (siempre obligatoria)
        f_a = request.form.get('fecha_nacimiento')
        if not f_a or not f_a.strip():
            flash('La fecha de nacimiento del alumno es obligatoria.', 'danger')
            return redirect(url_for('alumnos.inscripcion'))

        # 2. Determinar si se seleccionó un tutor existente (buscador) o hay que crear uno nuevo
        tutor_id = request.form.get('tutor_id', '').strip()

        if tutor_id:
            # --- Reutilizar tutor ya registrado ---
            tutor = Tutor.query.get(tutor_id)
            if not tutor:
                flash('El tutor seleccionado no existe. Volvé a buscarlo.', 'danger')
                return redirect(url_for('alumnos.inscripcion'))
        else:
            # --- Crear tutor nuevo: acá sí son obligatorios sus datos ---
            f_t = request.form.get('fecha_nacimiento_t')
            if not f_t or not f_t.strip():
                flash('La fecha de nacimiento del tutor es obligatoria.', 'danger')
                return redirect(url_for('alumnos.inscripcion'))

            legal = request.form.get('legal')
            l = (legal == 'True')

            tutor = Tutor(
                nombre=request.form['nombre_t'],
                apellido=request.form['apellido_t'],
                dni=request.form['dni_t'],
                fecha_nacimiento=dt.strptime(f_t.strip(), '%Y-%m-%d').date(),
                direccion=request.form['direccion_t'],
                telefono=request.form.get('telefono_t'),
                email=request.form.get('email_t'),
                genero=request.form['genero_t'],
                parentesco=request.form.get('parentesco'),
                ocupacion=request.form.get('ocupacion'),
                legal=l
            )
            db.session.add(tutor)

        # 3. Generar Legajo
        nuevo_legajo = generar_nuevo_legajo()

        # 4. Crear el Alumno
        nuevo_alumno = Alumno(
            nombre=request.form['nombre'],
            apellido=request.form['apellido'],
            dni=request.form['dni'],
            fecha_nacimiento=dt.strptime(f_a.strip(), '%Y-%m-%d').date(),
            direccion=request.form['direccion'],
            telefono=request.form.get('telefono'),
            email=request.form.get('email'),
            genero=request.form['genero'],
            cuil=request.form['cuil'],
            legajo=nuevo_legajo,
            id_colegio=colegio.id_colegio if colegio else None
        )
        db.session.add(nuevo_alumno)

        db.session.flush()  # para tener nuevo_alumno.id (y tutor.id si es nuevo)

        # 5. Vincular alumno y tutor en la tabla intermedia
        db.session.execute(
            alumno_tutor.insert().values(alumno_id=nuevo_alumno.id, tutor_id=tutor.id)
        )

        db.session.commit()

        flash('Alumno registrado exitosamente.', 'success')
        return redirect(url_for('alumnos.view', id=nuevo_alumno.id))

    except ValueError:
        db.session.rollback()
        flash('El formato de las fechas ingresadas no es válido.', 'danger')
        return redirect(url_for('alumnos.inscripcion'))

    except KeyError as e:
        db.session.rollback()
        flash(f'Falta completar el campo obligatorio: {str(e)}', 'danger')
        return redirect(url_for('alumnos.inscripcion'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error al registrar los datos: {str(e)}', 'danger')
        return redirect(url_for('alumnos.inscripcion'))


#funcion para calcular la edad del alumno
def calculateAge(birthDate):
    today = dt.today()
    age = today.year - birthDate.year - ((today.month, today.day) < (birthDate.month, birthDate.day))
    return age


@alumnos.route('/alumnos/view/<id>', methods=["GET"]) #detalle de alumno
def view(id):
    alumno = db.session.query(Alumno).options(joinedload(Alumno.tutores)).get(id)
    age = calculateAge(alumno.fecha_nacimiento)
    return render_template('/alumnos/detailAlumno.html', alumno=alumno, edad=age)


@alumnos.route('/alumnos/update/<alumno>', methods=["POST", "GET"])
def update_alumno(alumno):
    alumno = Alumno.query.get(alumno)
    if request.method == "POST":
        alumno.nombre = request.form['nombre']
        alumno.apellido = request.form['apellido']
        alumno.cuil = request.form['cuil']
        # Antes se guardaba el string crudo del form; se castea a date igual que en new_alumno
        alumno.fecha_nacimiento = dt.strptime(request.form['fecha_nacimiento'].strip(), '%Y-%m-%d').date()
        alumno.genero = request.form['genero']
        alumno.direccion = request.form['direccion']
        alumno.telefono = request.form['telefono']
        alumno.email = request.form['email']
        db.session.commit()
        flash('Datos Actualizados!')
        return redirect(url_for('alumnos.view', id=alumno.id))
    return render_template("/alumnos/updateAlumno.html", alumno=alumno)


@alumnos.route('/alumnos/update_tutor/<alumno>', methods=["POST", "GET"])
def update_tutor(alumno):
    alumno = Alumno.query.get(alumno)
    if request.method == "POST":
        for tutor in alumno.tutores:
            tutor.nombre = request.form['nombre_t']
            tutor.apellido = request.form['apellido_t']
            tutor.fecha_nacimiento = dt.strptime(request.form['fecha_nacimiento_t'].strip(), '%Y-%m-%d').date()
            tutor.genero = request.form['genero_t']
            tutor.direccion = request.form['direccion_t']
            tutor.telefono = request.form['telefono_t']
            tutor.email = request.form['email_t']
        db.session.commit()
        flash('Datos Actualizados!')
        return redirect(url_for('alumnos.view', id=alumno.id))
    return render_template("/alumnos/updateTutor.html", alumno=alumno)


#--------------------------------------------------------
# Buscador de tutores (AJAX)
#--------------------------------------------------------
@alumnos.route('/buscar-tutor')
def buscar_tutor():
    """Busca tutor por apellido o dni y devuelve todos sus datos
    para poder autocompletar el formulario en el frontend."""
    q = request.args.get('q', '').strip()

    if len(q) < 2:
        return {'tutores': []}

    tutores = Tutor.query.filter(
        db.or_(
            Tutor.apellido.ilike(f'%{q}%'),
            Tutor.dni.ilike(f'%{q}%')
        )
    ).order_by(Tutor.apellido, Tutor.nombre).limit(15).all()

    resultado = [
        {
            'id': t.id,
            'nombre': t.nombre,
            'apellido': t.apellido,
            'dni': t.dni,
            'direccion': t.direccion,
            'telefono': t.telefono,
            'email': t.email,
            'genero': t.genero,
            'parentesco': t.parentesco,
            'ocupacion': t.ocupacion,
            'legal': bool(t.legal),
            'fecha_nacimiento': t.fecha_nacimiento.isoformat() if t.fecha_nacimiento else '',
            'texto': f"{t.apellido}, {t.nombre} — DNI: {t.dni}"
        }
        for t in tutores
    ]
    return {'tutores': resultado}