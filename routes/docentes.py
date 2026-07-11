from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.colege import Docente, Colegio, Asignatura, Persona
from utils.db import db
from datetime import datetime

docentes = Blueprint("docentes", __name__)

@docentes.route('/docentes/home')
def home():
    #docentes = db.session.query(Docente).join(Persona).filter(Persona.id==Docente.id).all()
    #docentes = Docente.query.join(Persona).filter(Persona.id==Docente.id).all()
    docentes = Persona.query.filter(Persona.tipo_persona=="docente").all()
    #docentes = Docente.query.all()
    colegios = Colegio.query.all()
    return render_template('/docentes/home.html', docentes=docentes, colegios=colegios)

@docentes.route('/newDocente', methods=['POST'])
def new_docente():
    if request.method == 'POST':
        # 1. Capturar los datos enviados desde las etiquetas <input name="..."> de HTML
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        dni = request.form.get('dni')
        fecha_nac_str = request.form.get('fecha_nacimiento')
        direccion = request.form.get('direccion')
        telefono = request.form.get('telefono')
        email = request.form.get('email')
        genero = request.form.get('genero')
        id_colegio = request.form.get('id_colegio')
        cuil = request.form.get('dni')
        
        try:
            fecha_nacimiento = datetime.strptime(fecha_nac_str, '%Y-%m-%d').date()
            fecha_contratacion = None
        except ValueError:
            flash("El formato de fecha ingresado no es válido.", "danger")
            return render_template('/docentes/home.html')

        #new_docente = Docente(nombre, apellido, dni, fecha_nac, direccion, telefono, email, genero, id_colegio, cuil, cargo, fecha_contratacion, estado_contractual)
        new_docente = Docente(
            nombre=nombre.strip(),
            apellido=apellido.strip(),
            dni=dni.strip(),
            fecha_nacimiento=fecha_nacimiento,
            direccion=direccion.strip(),
            telefono=telefono.strip(),
            email=email.strip() or None,  # Si está vacío lo guarda como NULL
            genero=genero,
            id_colegio=int(id_colegio),
            cuil=cuil,
            cargo=None,
            fecha_contratacion=None,
            estado_contractual= None
        )
        db.session.add(new_docente)
        db.session.commit()
        flash('Docente añadido correctamente!')
        return redirect(url_for('docentes.home'))

@docentes.route('/searchDocente', methods=['POST'])
def searchDocente():
    if request.method == 'POST':
        tag = request.form.get('tag')
        if not tag:
            flash('Por favor, ingrese un apellido para buscar.', 'warning')
            return redirect(url_for('docentes.home'))
        
        # Realizamos la búsqueda usando LIKE para permitir coincidencias parciales
        docentes = Persona.query.filter(Persona.tipo_persona=="docente", Persona.apellido.ilike(f'%{tag}%')).all()
        
        if not docentes:
            flash(f'No se encontraron docentes con el apellido "{tag}".', 'info')
        
        colegios = Colegio.query.all()
        return render_template('/docentes/home.html', docentes=docentes, colegios=colegios)
    else:
        flash('Método de solicitud no permitido.', 'danger')
        return redirect(url_for('docentes.home'))

@docentes.route('/docentes/view/<id>', methods=['GET'])
def view(id):
    docente = Docente.query.get(id)
    return render_template('/docentes/view.html', docente=docente)

@docentes.route("/docentes/updateDocente/<id>", methods=['POST', 'GET'])
def updateDocente(id):
    docente = db.session.get(Docente, id)
    
    if not docente:
        flash('El docente solicitado no existe.', 'error')
        return redirect(url_for('docentes.home')) # Mejor usar redirect aquí

    if request.method == 'POST':
        try:
            # Usamos .get() y mantenemos el valor actual si el form viene vacío/None
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

            # Manejo seguro de fechas (solo se actualizan si el string no está vacío)
            fecha_nacimiento_str = request.form.get('fecha_nacimiento')
            if fecha_nacimiento_str:
                docente.fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, '%Y-%m-%d').date()

            fecha_contratacion_str = request.form.get('fecha_contratacion')
            if fecha_contratacion_str:
                docente.fecha_contratacion = datetime.strptime(fecha_contratacion_str, '%Y-%m-%d').date()

            db.session.commit()
            flash('¡Datos Actualizados con éxito!', 'success')
            
            # Patrón PRG: Redirigir en lugar de renderizar directamente tras un POST
            return redirect(url_for('docentes.view', id=docente.id))

        except ValueError:
            db.session.rollback()
            flash("El formato de fecha ingresado no es válido.", "danger")
            return redirect(url_for('docentes.updateDocente', id=docente.id))
    # Método GET: Mostrar el formulario con los datos actuales
    # Solo pasamos 'docente', no 'docente.id'
    return render_template("/docentes/updateDocente.html", docente=docente)

@docentes.route("/deleteDocente/<id>", methods=["POST"])
def deleteDocente(id):
    # 2. Uso de la sintaxis moderna
    docente = db.session.get(Docente, id)
    
    # 3. Validación de existencia
    if not docente:
            flash('El docente que intenta eliminar no existe o ya fue borrado.', 'danger')
            return redirect(url_for('docentes.home'))
            
    try:
            # 4. Intento de eliminación segura
            db.session.delete(docente)
            db.session.commit()
            flash(f'¡Docente "{docente.nombre} {docente.apellido}" borrado con éxito!', 'success')
            
    except Exception as e:
            # 5. Si hay registros hijos vinculados o falla la DB, evitamos el colapso
            db.session.rollback()
            flash('No se pudo eliminar el docente. Asegúrese de que no tenga materias o cargos asociados.', 'danger')
            print(f"Error en la eliminación: {str(e)}") # Útil para ti en la consola
        
    return redirect(url_for('docentes.home'))