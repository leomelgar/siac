from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.colege import Alumno, Tutor, Matricula, Curso, Legajo
from utils.db import db
from datetime import date

alumnos = Blueprint("alumnos", __name__)

# @alumnos.route('/alumnos/home', methods=["POST","GET"]) #listado de alumnos
# def home():
#     alumnos = Alumno.query.all()
#     if request.method == "POST" and 'tag' in request.form:
#         tag = request.form['tag']
#         search = "%{}%".format(tag)
#         alumnos = Alumno.query.filter(Alumno.apellido.like(search))
#         if not alumnos:
#             flash('No existe registro...')
#         else:
#             return render_template('/alumnos/home.html', alumnos=alumnos)
#     return render_template('/alumnos/home.html', alumnos=alumnos)

@alumnos.route('/alumnos/home/<estado>', methods=["POST","GET"]) #listado de alumnos
def home(estado):
    if estado=="1":#pre-inscriptos
        alumnos = Alumno.query.filter(Alumno.inscripto.like('1'))
        cantidad = Alumno.query.filter(Alumno.inscripto==1).count()
        title = "Pre Insriptos"
        if request.method == "POST" and 'tag' in request.form:
            tag = request.form['tag']
            search = "%{}%".format(tag)
            alumnos = alumnos.filter(Alumno.apellido.like(search))
            cantidad = alumnos.count()
            if not alumnos:
                flash('No existe registro...')
            else:
                return render_template('/alumnos/home.html', estado=1, alumnos=alumnos, cantidad=cantidad, title=title)
        return render_template('/alumnos/home.html', estado=1, alumnos=alumnos,cantidad=cantidad, title=title)
    else:#alumnos inscriptos
        alumnos = Alumno.query.filter(Alumno.inscripto.like('0'))
        cantidad = Alumno.query.filter(Alumno.inscripto==0).count()
        title = "Alumnos"
        if request.method == "POST" and 'tag' in request.form:
            tag = request.form['tag']
            search = "%{}%".format(tag)
            alumnos = alumnos.filter(Alumno.apellido.like(search))
            cantidad = alumnos.count()
            if not alumnos:
                flash('No existe registro...')
            else:
                return render_template('/alumnos/home.html', estado=0, alumnos=alumnos, cantidad=cantidad, title=title)
        return render_template('/alumnos/home.html', estado=0, alumnos=alumnos, cantidad=cantidad, title=title)

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
    legajo = Legajo.query.filter_by(fk_alumno_id=alumno.idAlumno).first()
    matricula = Matricula.query.filter_by(fk_legajo_id=legajo.idLegajo).first()
    tutor = Tutor.query.get(alumno.tutor_id)
    return render_template('/alumnos/detailAlumno.html', alumno=alumno, age=age, tutor=tutor, matricula=matricula, legajo=legajo)

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
        cuil = request.form['cuil']
        parentesco = request.form['parentesco']
        direccion = request.form['direccion']
        telefono  = request.form['telefono']
        email = request.form['email']


        new_tutor = Tutor(nombre, apellido, cuil, parentesco, direccion, telefono, email)
        db.session.add(new_tutor)
        db.session.commit()
        flash('Tutor Agregado Correctamente!')
        return render_template('/alumnos/new.html', tutor=new_tutor)

@alumnos.route('/newAlumno', methods=['POST'])
def new_alumno():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        cuil = request.form['cuil']
        fechaNac = request.form['fechaNac']
        lugarNac = request.form['lugarNac']
        sexo = request.form['sexo']
        direccion = request.form['direccion']
        telefono  = request.form['telefono']
        email = request.form['email']
        fechaPreinscripcion = date.today()#se guarda en el legajo en primera instancia, luego es reemplazado por la fecha de inscripcion definitiva
        condicionIngreso = request.form['condicionIngreso']#se guarda en el legajo
        colegioAnterior = request.form['colegioAnterior']
        inscripto = '1'
        tutor_id = request.form['tutor_id']

        new_alumno = Alumno(nombre, apellido, cuil, fechaNac, lugarNac, sexo, direccion, telefono, email, inscripto, tutor_id)
        db.session.add(new_alumno)
        db.session.commit()
        new_legajo = Legajo(fechaPreinscripcion, condicionIngreso, None, None, colegioAnterior, new_alumno.idAlumno)
        db.session.add(new_legajo)
        db.session.commit()
        flash('Pre-Inscripcion realizada!')
        #return render_template('/alumnos/view.html', alumno=alumno)
        return redirect(url_for('alumnos.view', alumno=new_alumno.idAlumno))

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

@alumnos.route('/alumnos/matricula/<alumno_id>', methods=["POST", "GET"])
def matricular(alumno_id):
    alumno = Alumno.query.get(alumno_id)
    legajo = Legajo.query.filter_by(fk_alumno_id=alumno_id).first()
    print(legajo)
    cursos = Curso.query.order_by(Curso.nombre_curso)#listar todos los cursos por orden ascendente
    if alumno.inscripto=="1":#pre-inscriptos, va pasar a ser alumno del colegio
        if request.method == "POST":
            fechaInscripcion = request.form['fechaInscripcion']#esta fecha es la de admision al colegio y se guarda en el legajo
            añoAcademico = request.form['añoAcademico']
            #condicionIngreso = request.form['condicionIngreso']
            #alumno_id = alumno_id
            colegio_id = 8 #falta añadir logica para asignar el colegio
            curso_id = request.form['curso_id']

            new_matricula = Matricula(fechaInscripcion, añoAcademico, colegio_id, curso_id, legajo.idLegajo)
            db.session.add(new_matricula)
            legajo.fechaAdmision=fechaInscripcion
            legajo.condicionAlumno="regular"
            alumno.inscripto = '0'
            db.session.commit()

            flash('matricula realizada correctamente, ya es Alumno!')
            return redirect(url_for('alumnos.home', estado=0))
        return render_template('/alumnos/matricula.html', alumno=alumno, cursos=cursos)
    else:
        if request.method == "POST":
            fechaInscripcion = request.form['fechaInscripcion']
            añoAcademico = request.form['añoAcademico']
            condicionIngreso = request.form['condicionIngreso']
            #alumno_id = alumno_id
            colegio_id = 8 #falta añadir logica para asignar el colegio
            curso_id = request.form['curso_id']

            new_matricula = Matricula(fechaInscripcion, añoAcademico, condicionIngreso, colegio_id, curso_id)
            db.session.add(new_matricula)
            db.session.commit()

            flash('matricula realizada correctamente, ya es Alumno!')
            return redirect(url_for('alumnos.home', estado=0))
        return render_template('/alumnos/matricula.html', alumno=alumno, cursos=cursos)


@alumnos.route('/alumnos/updateMatricula/<matricula>', methods=["POST","GET"])
def update_matricula(matricula):
    matricula = Matricula.query.get(matricula)
    legajo = Legajo.query.filter_by(idLegajo=matricula.fk_legajo_id).first()
    alumno = Alumno.query.filter_by(idAlumno=legajo.fk_alumno_id).first()
    cursos = Curso.query.all()
    curso = Curso.query.get(matricula.curso_id)
    if request.method == "POST":
        matricula.fechaInscripcion = request.form['fechaInscripcion']
        matricula.añoAcademico = request.form['añoAcademico']
        matricula.curso_id = request.form['curso_id']

        db.session.commit()
        flash('Datos Actualizados!')
        return redirect(url_for('alumnos.detailAlumno', alumno=alumno.idAlumno))
    return render_template("/alumnos/updateMatricula.html", matricula=matricula, alumno=alumno, curso=curso, cursos=cursos)
