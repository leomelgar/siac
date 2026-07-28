from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models.colege import Docente, Colegio, Asignatura, Persona
from utils.db import db
from datetime import datetime
from routes.decorators import permiso_requerido

docentes = Blueprint("docentes", __name__)

@docentes.before_request
@login_required
def requerir_login():
    pass

@docentes.route('/docentes/home')
def home():
    tag_busqueda = request.args.get('tag', '').strip()
    if tag_busqueda:
        docentes_db = Docente.query.filter(
            (Docente.apellido.ilike(f'%{tag_busqueda}%'))).all()
    else:
        docentes_db = Docente.query.all()

    lista_docentes = [d.to_dict() for d in docentes_db]
    cantidad = len(lista_docentes)
    return render_template('/docentes/home.html',
                           docentes=lista_docentes,
                           cantidad=cantidad)

@docentes.route('/newDocente', methods=['POST'])
@permiso_requerido('CARGAR_DOCENTE')
def new_docente():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '')
        apellido = request.form.get('apellido', '')
        dni = request.form.get('dni', '')
        fecha_nac_str = request.form.get('fecha_nacimiento')
        direccion = request.form.get('direccion', '')
        telefono = request.form.get('telefono', '')
        email = request.form.get('email', '')
        genero = request.form.get('genero')
        cuil = request.form.get('dni', '')

        try:
            if not fecha_nac_str:
                raise ValueError("La fecha de nacimiento es obligatoria.")
            fecha_nacimiento = datetime.strptime(fecha_nac_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            flash("El formato de fecha ingresado no es válido o está vacío.", "danger")
            # Antes: render_template('docentes/home.html') sin pasar 'docentes' ni 'cantidad',
            # lo cual rompe el template si espera esas variables. Redirigimos en su lugar.
            return redirect(url_for('docentes.home'))

        new_docente = Docente(
            nombre=nombre.strip(),
            apellido=apellido.strip(),
            dni=dni.strip(),
            fecha_nacimiento=fecha_nacimiento,
            direccion=direccion.strip(),
            telefono=telefono.strip(),
            email=email.strip() or None,
            genero=genero,
            id_colegio=1,
            cuil=cuil,
            cargo=None,
            fecha_contratacion=None,
            estado_contractual=None
        )

        try:
            db.session.add(new_docente)
            db.session.commit()
            flash('Docente añadido correctamente!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('No se pudo guardar el docente. Verificá que el DNI/CUIL no esté repetido.', 'danger')
            print(f"Error al crear docente: {str(e)}")

        return redirect(url_for('docentes.home'))

def calcular_edad(fecha_nacimiento):
    hoy = datetime.today()
    return hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))

@docentes.route('/docentes/view/<id>', methods=['GET'])
def view(id):
    docente = Docente.query.get(id)

    if not docente:
        flash('El docente solicitado no existe.', 'danger')
        return redirect(url_for('docentes.home'))

    edad = calcular_edad(docente.fecha_nacimiento)
    return render_template('/docentes/view.html', docente=docente, edad=edad)

@docentes.route("/docentes/updateDocente/<id>", methods=['POST', 'GET'])
@permiso_requerido('CARGAR_DOCENTE')
def updateDocente(id):
    docente = db.session.get(Docente, id)

    if not docente:
        flash('El docente solicitado no existe.', 'danger')
        return redirect(url_for('docentes.home'))

    if request.method == 'POST':
        try:
            docente.nombre = request.form.get('nombre') or docente.nombre
            docente.apellido = request.form.get('apellido') or docente.apellido
            docente.dni = request.form.get('dni') or docente.dni
            docente.direccion = request.form.get('direccion') or docente.direccion
            docente.telefono = request.form.get('telefono') or docente.telefono
            docente.email = request.form.get('email') or docente.email
            docente.genero = request.form.get('genero') or docente.genero
            docente.cuil = request.form.get('cuil') or docente.cuil
            docente.cargo = request.form.get('cargo') or docente.cargo
            docente.estado_contractual = request.form.get('estado_contractual') or docente.estado_contractual

            fecha_nacimiento_str = request.form.get('fecha_nacimiento')
            if fecha_nacimiento_str:
                docente.fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, '%Y-%m-%d').date()

            fecha_contratacion_str = request.form.get('fecha_contratacion')
            if fecha_contratacion_str:
                docente.fecha_contratacion = datetime.strptime(fecha_contratacion_str, '%Y-%m-%d').date()

            db.session.commit()
            flash('¡Datos Actualizados con éxito!', 'success')
            return redirect(url_for('docentes.view', id=docente.id))

        except ValueError:
            db.session.rollback()
            flash("El formato de fecha ingresado no es válido.", "danger")
            return redirect(url_for('docentes.updateDocente', id=docente.id))

    return render_template("/docentes/updateDocente.html", docente=docente)

@docentes.route("/deleteDocente/<id>", methods=["POST"])
@permiso_requerido('CARGAR_DOCENTE')
def deleteDocente(id):
    docente = db.session.get(Docente, id)

    if not docente:
        flash('El docente que intenta eliminar no existe o ya fue borrado.', 'danger')
        return redirect(url_for('docentes.home'))

    try:
        db.session.delete(docente)
        db.session.commit()
        flash(f'¡Docente "{docente.nombre} {docente.apellido}" borrado con éxito!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('No se pudo eliminar el docente. Asegúrese de que no tenga materias o cargos asociados.', 'danger')
        print(f"Error en la eliminación: {str(e)}")

    return redirect(url_for('docentes.home'))