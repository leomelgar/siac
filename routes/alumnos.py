from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.colege import Alumno, Tutor, Persona
from utils.db import db
from datetime import date

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
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        dni = request.form['dni']
        telefono  = request.form['telefono']
        email = request.form['email']
        direccion = request.form['direccion']
        parentesco = request.form['parentesco']
        legal = request.form['legal']
    
        new_tutor = Tutor(nombre, apellido, dni, telefono, email, direccion, parentesco, legal)
        db.session.add(new_tutor)
        db.session.commit()
        flash('Tutor añadido correctamente!')
        #return render_template('/alumnos/new.html')
        return redirect(url_for('alumnos.home'))

@alumnos.route('/newAlumno', methods=['POST'])
def new_alumno():
    if request.method == 'POST':
        #------------datos de alumno ------------
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        cuil = request.form['cuil']
        fechaNac = request.form['fechaNac']
        sexo = request.form['sexo']
        direccion = request.form['direccion']
        telefono  = request.form['telefono']
        email = request.form['email']
        #tutor_id = request.form['tutor_id']

        new_alumno = Alumno(nombre, apellido, cuil, fechaNac, sexo, direccion, telefono, email, new_tutor.id_Tutor)
        db.session.add(new_alumno)
        db.session.add(new_tutor)
        db.session.commit()
        flash('Datos guardados correctamente!')
        #return render_template('/alumnos/view.html', alumno=alumno)
        return redirect(url_for('alumnos.view', alumno=new_alumno.idAlumno))