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
        """ nombre = request.form['nombre']
        apellido = request.form['apellido']
        dni = request.form['dni']
        fecha_nac = request.form['fecha_nac']
        direccion = request.form['direccion']
        cargo = request.form['cargo']
        telefono  = request.form['telefono']
        email = request.form['email']
        id_colegio = request.form['id_colegio']
        fecha_contratacion = request.form['fecha_contratacion']
        estado_contractual = request.form['estado_contractual']
        cuil = request.form['dni'] """
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

@docentes.route('/docentes/view/<id>', methods=['GET'])
def view(id):
    docente = Docente.query.get(id)
    return render_template('/docentes/view.html', docente=docente)

@docentes.route("/docentes/updateDocente/<id>", methods=['POST', 'GET'])
def updateDocente(id):
    docente = Docente.query.get(id)
    if not docente:
        flash('El docente solicitado no existe.', 'error')
        return render_template('/docentes/home.html')
    if request.method == 'POST':
        docente.nombre = request.form['nombre']
        docente.apellido = request.form['apellido']
        docente.dni = request.form['dni']
        docente.fecha_nacimiento = request.form['fecha_nacimiento']
        docente.direccion = request.form['direccion']
        docente.telefono = request.form['telefono']
        docente.email = request.form['email']
        docente.genero = request.form['genero']
        docente.cuil = request.form['cuil']
    #     new_nombre = request.form.get('nombre')
    #     new_apellido = request.form.get('apellido')
    #     new_dni = request.form.get('dni')
    #     new_fecha_nacimiento_str = request.form.get('fecha_nacimiento')
    #     new_direccion = request.form.get('direccion')
    #     new_telefono = request.form.get('telefono')
    #     new_email = request.form.get('email')
    #     new_genero = request.form.get('genero')
    #     new_cuil = request.form.get('cuil')
    #     print(f"Datos recibidos: nombre={new_nombre}, apellido={new_apellido}, dni={new_dni}, fecha_nacimiento={new_fecha_nacimiento_str}, direccion={new_direccion}, telefono={new_telefono}, email={new_email}, genero={new_genero}, cuil={new_cuil}")
    # # Validar y convertir la fecha de nacimiento
    #     try:
    #         if new_fecha_nacimiento_str:
    #             new_fecha_nacimiento = datetime.strptime(new_fecha_nacimiento_str, '%Y-%m-%d')
    #         else:
    #             new_fecha_nacimiento = request.form.get('fecha_nacimiento')
    #     except ValueError:
    #         flash('Formato de fecha de nacimiento inválido. Use AAAA-MM-DD.', 'error')
    #         return render_template("/docentes/updateDocente.html", docente=docente)

    #     docente.nombre = new_nombre
    #     docente.apellido = new_apellido
    #     docente.dni = new_dni
    #     docente.fecha_nacimiento = new_fecha_nacimiento
    #     docente.direccion = new_direccion
    #     docente.telefono = new_telefono
    #     docente.email = new_email
    #     docente.genero = new_genero
    #     docente.cuil = new_cuil
        print(f"Datos actualizados: nombre={docente.nombre}, apellido={docente.apellido}, dni={docente.dni}, fecha_nacimiento={docente.fecha_nacimiento}, direccion={docente.direccion}, telefono={docente.telefono}, email={docente.email}, genero={docente.genero}, cuil={docente.cuil}, id={docente.id}")
        db.session.commit()
        flash('Datos Actualizados!')
        return redirect(url_for('docentes.home'))
    print(f"Datos Actuales: nombre={docente.nombre}, apellido={docente.apellido}, dni={docente.dni}, fecha_nacimiento={docente.fecha_nacimiento}, direccion={docente.direccion}, telefono={docente.telefono}, email={docente.email}, genero={docente.genero}, cuil={docente.cuil}, id={docente.id}")
    return render_template("/docentes/updateDocente.html", docente=docente)

@docentes.route("/deleteDocente/<id>", methods=["GET"])
def deleteDocente(id):
    docente = Docente.query.get(id)
    db.session.delete(docente)
    db.session.commit()
    flash('Docente Borrado!')
    return redirect(url_for('docentes.home'))
