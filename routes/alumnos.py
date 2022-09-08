from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.colege import Alumno, Tutor
from utils.db import db

alumnos = Blueprint("alumnos", __name__)

@alumnos.route('/alumnos/home')
def home():
    alumnos = Alumno.query.all()
    return render_template('/alumnos/home.html', alumnos=alumnos)

@alumnos.route('/inscripcion')
def inscripcion():
     return render_template('/alumnos/new.html')

@alumnos.route('/newTutor', methods=['POST'])
def new_tutor():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        cuil = request.form['cuil']
        parentezco = request.form['parentezco']
        direccion = request.form['direccion']
        telefono  = request.form['telefono']
        email = request.form['email']

        new_tutor = Tutor(nombre, apellido, cuil, parentezco, direccion, telefono, email)
        db.session.add(new_tutor)
        db.session.commit()
        flash('Tutor Agregado Correctamente!')
        return render_template('/alumnos/new.html', tutor=new_tutor.idTutor)

@alumnos.route('/newAlumno', methods=['POST'])
def new_alumno():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        cuil = request.form['cuil']
        fechaNac = request.form['fechaNac']
        sexo = request.form['sexo']
        direccion = request.form['direccion']
        telefono  = request.form['telefono']
        email = request.form['email']
        tutor_id = request.form['idTutor']
        #fechaInscripcion = request.form['fechaInscripcion']
        #reInscripcion = "2022/09/09" #realizar correccion. ver el tema de un alumno cuando se reinscribe
        #añoCursada = "primer" #realizar correccion para asignar el año de cursada
        #colegio_id = 8 #realizar correccion para asignar colegio

        new_alumno = Alumno(nombre, apellido, cuil, fechaNac, sexo, direccion, telefono, email, tutor_id)
        db.session.add(new_alumno)
        db.session.commit()
        flash('Alumno Añadido Correctamente!')
        return redirect(url_for('alumnos.home'))
