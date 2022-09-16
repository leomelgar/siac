from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.colege import Alumno, Tutor, Matricula
from utils.db import db
from datetime import date

alumnos = Blueprint("alumnos", __name__)

@alumnos.route('/alumnos/home') #listado de alumnos
def home():
    alumnos = Alumno.query.all()
    return render_template('/alumnos/home.html', alumnos=alumnos)

@alumnos.route('/alumnos/view/<alumno>', methods=["POST", "GET"]) #vista de alumno luego de pre-inscripcion, deriva a la vista para matricular
def view(alumno):
    alumno = Alumno.query.get(alumno)
    return render_template('/alumnos/view.html', alumno=alumno)

def calculateAge(birthDate):#funcion para calcular la edad del alumno
    today = date.today()
    age = today.year-birthDate.year-((today.month, today.day)<(birthDate.month, birthDate.day))
    return age

@alumnos.route('/alumnos/detailAlumno/<alumno>', methods=["POST","GET"])
def detailAlumno(alumno):
    alumno = Alumno.query.get(alumno)
    age = calculateAge(alumno.fechaNac)
    matricula = Matricula.query.filter_by(alumno_id=alumno.idAlumno).first()
    tutor = Tutor.query.get(alumno.tutor_id)
    return render_template('/alumnos/detailAlumno.html', alumno=alumno, age=age, matricula=matricula, tutor=tutor)

@alumnos.route('/inscripcion', methods=["POST","GET"])
@alumnos.route('/inscripcion/<tutor>', methods=["POST","GET"])
def inscripcion():
    # if request.method == "POST":

    # tutores = Tutor.query.order_by(Tutor.apellido.asc())
    if request.method == "POST" and 'tag' in request.form:
        tag = request.form['tag']
        search = "%{}%".format(tag)
        #tutores = Tutor.query.filter_by(apellido=search).first()
        tutores = Tutor.query.filter(Tutor.apellido.like(search))
        return render_template('/alumnos/new.html', tutores=tutores, tag=tag)
    return render_template('/alumnos/new.html')

@alumnos.route('/newTutor', methods=['POST'])
def new_tutor():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        cuil = request.form['cuil']
        parentesco = request.form['parentesco']
        direccion = request.form['direccion']
        telefono  = request.form['telefono']
        email = request.form['email']

        new_tutor = Tutor(nombre, apellido, cuil, parentesco, direccion, telefono, email)
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
        tutor_id = request.form['tutor_id']

        new_alumno = Alumno(nombre, apellido, cuil, fechaNac, sexo, direccion, telefono, email, tutor_id)
        db.session.add(new_alumno)
        db.session.commit()
        flash('Pre-Inscripcion realizada!')
        #return render_template('/alumnos/view.html', alumno=alumno)
        return redirect(url_for('alumnos.view', alumno=new_alumno.idAlumno))

@alumnos.route('/alumnos/matricula/<alumno>', methods=["POST", "GET"])
def matricular(alumno):
    if request.method == "POST":
        fechaInscripcion = request.form['fechaInscripcion']
        reInscripcion = request.form['reInscripcion']
        añoAcademico = request.form['añoAcademico']
        condicionIngreso = request.form['condicionIngreso']
        alumno_id = alumno
        colegio_id = 8

        new_matricula = Matricula(fechaInscripcion, reInscripcion, añoAcademico, condicionIngreso, alumno_id, colegio_id)
        db.session.add(new_matricula)
        db.session.commit()
        flash('matricula realizada correctamente, ya es Alumno!')
        return redirect(url_for('alumnos.home'))
    return render_template('/alumnos/matricula.html', alumno=alumno)
