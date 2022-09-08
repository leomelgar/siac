from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.colege import Alumno, Colegio
from utils.db import db

alumnos = Blueprint("alumnos", __name__)

@alumnos.route('/alumnos/home')
def home():
    alumnos = Alumno.query.all()
    return render_template('/alumnos/home.html', alumnos=alumnos)

@alumnos.route('/newAlumno', methods=['POST'])
def new_alumno():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        cuil = request.form['cuil']
        fechaNac = request.form['fechaNac']
        direccion = request.form['direccion']
        telefono  = request.form['telefono']
        email = request.form['email']
        fechaInscripcion = request.form['fechaInscripcion']
        reInscripcion = "2022/09/09" #realizar correccion. ver el tema de un alumno cuando se reinscribe
        añoCursada = "primer" #realizar correccion para asignar el año de cursada
        colegio_id = 8 #realizar correccion para asignar colegio

        new_alumno = Alumno(nombre, apellido, cuil, fechaNac, direccion, telefono, email, fechaInscripcion, reInscripcion, añoCursada, colegio_id)
        db.session.add(new_alumno)
        db.session.commit()
        flash('Alumno Añadido Correctamente!')
        return redirect(url_for('alumnos.home'))
