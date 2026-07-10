from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.colege import Alumno, Tutor, Persona, Colegio
from utils.db import db
from datetime import datetime

alumnos = Blueprint("alumnos", __name__)

@alumnos.route('/alumnos/home', methods=["POST","GET"]) #listado de alumnos
def home():
    alumnos = Alumno.query.all()
    if request.method == "POST" and 'tag' in request.form:
        tag = request.form['tag']
        search = "%{}%".format(tag)
        alumnos = Alumno.query.filter(Alumno.apellido.like(search))
        if not alumnos:
            flash('No existe registro...')
        else:
            return render_template('/alumnos/home.html', alumnos=alumnos)
    return render_template('/alumnos/home.html', alumnos=alumnos)

@alumnos.route('/inscripcion')
#@alumnos.route('/inscripcion/<tutor>', methods=["POST","GET"])
def inscripcion():
    return render_template('/alumnos/new.html')

@alumnos.route('/newTutor', methods=['POST'])
def new_tutor():
    # if request.method == 'POST':
    #     nombre = request.form['nombre']
    #     apellido = request.form['apellido']
    #     dni = request.form['dni']
    #     telefono  = request.form['telefono']
    #     email = request.form['email']
    #     direccion = request.form['direccion']
    #     parentesco = request.form['parentesco']
    #     legal = request.form['legal']
    
    #     new_tutor = Tutor(nombre, apellido, dni, telefono, email, direccion, parentesco, legal)
    #     db.session.add(new_tutor)
    #     db.session.commit()
    #     flash('Tutor añadido correctamente!')
    #     #return render_template('/alumnos/new.html')
    #     return redirect(url_for('alumnos.home'))
    if request.method == 'POST':
        try:
            # Capturar datos del formulario HTML
            fecha_nac = datetime.strptime(request.form['fecha_nacimiento'], '%Y-%m-%d').date()
            
            # Los checkboxes en HTML envían "on" si están marcados, o nada si no lo están
            es_legal = request.form.get('legal') == 'on'
            
            nuevo_tutor = Tutor(
                nombre=request.form['nombre'],
                apellido=request.form['apellido'],
                dni=request.form['dni'],
                fecha_nacimiento=fecha_nac,
                direccion=request.form['direccion'],
                telefono=request.form.get('telefono'),
                email=request.form.get('email'),
                genero=request.form['genero'],
                parentesco=request.form.get('parentesco'),
                ocupacion=request.form.get('ocupacion'),
                legal=es_legal
            )
            
            db.session.add(nuevo_tutor)
            db.session.commit()
            
            flash('Tutor creado exitosamente.', 'success')
            return redirect(url_for('listar_tutores'))

        except IntegrityError:
            db.session.rollback()
            flash('Error: El DNI o Email ya se encuentra registrado.', 'danger')
        except Exception as e:
            flash(f'Error al crear el tutor: {str(e)}', 'danger')

    # Si es GET (acaba de entrar a la URL), mostramos el formulario vacío
    return render_template('alumnos.home.html')

@alumnos.route('/newAlumno', methods=['POST'])
def new_alumno():
    # if request.method == 'POST':
    #     #------------datos de alumno ------------
    #     nombre = request.form['nombre']
    #     apellido = request.form['apellido']
    #     cuil = request.form['cuil']
    #     fechaNac = request.form['fechaNac']
    #     sexo = request.form['sexo']
    #     direccion = request.form['direccion']
    #     telefono  = request.form['telefono']
    #     email = request.form['email']
    #     #tutor_id = request.form['tutor_id']

    #     new_alumno = Alumno(nombre, apellido, cuil, fechaNac, sexo, direccion, telefono, email, new_tutor.id_Tutor)
    #     db.session.add(new_alumno)
    #     db.session.add(new_tutor)
    #     db.session.commit()
    #     flash('Datos guardados correctamente!')
    #     #return render_template('/alumnos/view.html', alumno=alumno)
    #     return redirect(url_for('alumnos.view', alumno=new_alumno.idAlumno))
    colegios = Colegio.query.all()
    if request.method == 'POST':
        # Procesamos la fecha de nacimiento que viene como string 'YYYY-MM-DD'
        fecha_nac_str = request.form['fecha_nacimiento']
        
        nuevo_alumno = Alumno(
            # Campos heredados de Persona
            nombre=request.form['nombre'],
            apellido=request.form['apellido'],
            dni=request.form['dni'],
            fecha_nacimiento=datetime.strptime(fecha_nac_str, '%Y-%m-%d').date(),
            direccion=request.form['direccion'],
            telefono=request.form['telefono'],
            email=request.form['email'],
            genero=request.form['genero'],
            
            # Campos propios de Alumno
            cuil=request.form['cuil'],
            legajo=request.form['legajo'],
            id_colegio=request.form['id_colegio']
        )
        db.session.add(nuevo_alumno)
        db.session.commit()
        return redirect(url_for('alumnos.home'))
        
    return render_template('newAlumno.html', colegios=colegios, alumno=None)