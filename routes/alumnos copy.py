from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.colege import Alumno, Tutor, Matricula
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

@alumnos.route('/searchTutor', methods=['POST'])#buscar un tutor antes de tomar los datos del futuro alumno
def search_tutor():
    #if request.method == "POST" and 'tag' in request.form:
    if request.method == "POST":
        tag = request.form['tag']
        search = "%{}%".format(tag)
        #tutor = Tutor.query.filter_by(apellido=search).first()
        tutores = Tutor.query.filter(Tutor.apellido.like(search))
        return render_template('/alumnos/new.html', tutores=tutores, tag=tag)

@alumnos.route('/inscripcionConTutor/<tutor>', methods=["POST","GET"])
def inscripcion_tutor(tutor):
    t = Tutor.query.get(tutor)
    print(t.apellido)
    return render_template('/alumnos/new.html', tutor=t)


@alumnos.route('/inscripcion')
#@alumnos.route('/inscripcion/<tutor>', methods=["POST","GET"])
def inscripcion():
    # tutores = Tutor.query.order_by(Tutor.apellido.asc())
    #if request.method == "POST":
    #     tag = request.form['tag']
    #     search = "%{}%".format(tag)
    #     tutores = Tutor.query.filter(Tutor.apellido.like(search))
    #     return render_template('/alumnos/new.html', tutor=tutor)
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

@alumnos.route('/alumnos/matricula/<alumno_id>', methods=["POST", "GET"])
def matricular(alumno_id):
    alumno = Alumno.query.get(alumno_id)
    if request.method == "POST":
        fechaInscripcion = request.form['fechaInscripcion']
        reInscripcion = request.form['reInscripcion']
        añoAcademico = request.form['añoAcademico']
        condicionIngreso = request.form['condicionIngreso']
        alumno_id = alumno_id
        colegio_id = 8 #falta añadir logica para asignar el colegio

        new_matricula = Matricula(fechaInscripcion, reInscripcion, añoAcademico, condicionIngreso, alumno_id, colegio_id)
        db.session.add(new_matricula)
        db.session.commit()
        flash('matricula realizada correctamente, ya es Alumno!')
        return redirect(url_for('alumnos.home'))
    return render_template('/alumnos/matricula.html', alumno=alumno)

@alumnos.route('/alumnos/update/<alumno>', methods=["POST","GET"])
def update_alumno(alumno):
    alumno = Alumno.query.get(alumno)
    if request.method == "POST":
        alumno.nombre = request.form['nombre']
        alumno.apellido = request.form['apellido']
        alumno.cuil = request.form['cuil']
        alumno.fechaNac = request.form['fechaNac']
        alumno.sexo = request.form['sexo']
        alumno.direccion = request.form['direccion']
        alumno.telefono = request.form['telefono']
        alumno.email = request.form['email']
        db.session.commit()
        flash('Datos Actualizados!')
        return redirect(url_for('alumnos.detailAlumno', alumno=alumno.idAlumno))
    return render_template("/alumnos/updateAlumno.html", alumno=alumno)
