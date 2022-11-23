from crypt import methods
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.colege import Curso, Alumno, Aula, Docente, Turno, Matricula, Horario
from utils.db import db
import math

cursos = Blueprint("cursos", __name__)

@cursos.route('/cursos/home')
def home():
    #cursos = Curso.query.all()
    #cursos = Curso.query.join(Aula, Curso.aula_id==Aula.idAula).add_columns(Curso.curso, Curso.division, Curso.periodo, Aula.nombre)
    #consulta = "SELECT * FROM contactsdb.curso JOIN contactsdb.aula ON contactsdb.curso.aula_id = contactsdb.aula.idAula"
    #cursos = db.session.execute(consulta)
    cursos = Curso.query.join(Aula, Curso.aula_id==Aula.idAula).join(Turno, Curso.turno_id==Turno.idTurno).add_columns(Curso.idCurso, Curso.nombre_curso, Curso.division, Curso.periodo, Aula.nombre, Aula.capacidad, Aula.ubicacion, Turno.turno).order_by(Curso.nombre_curso)
    
    return render_template('/cursos/home.html', cursos=cursos)

@cursos.route('/cursos/nuevo', methods=["POST","GET"])
def new():
    aulas = Aula.query.all()
    turnos = Turno.query.all()
    return render_template('/cursos/curso.html', aulas=aulas, turnos=turnos)

@cursos.route('/cursos/add_curso', methods=["POST"])
def add_curso():
    if request.method=="POST":
        nombre_curso = request.form['nombre_curso']
        division = request.form['division']
        periodo = request.form['periodo']
        aula_id = request.form['aula_id']
        turno_id = request.form['turno_id']
       
        new_curso = Curso(nombre_curso, division, periodo, aula_id, turno_id)
        db.session.add(new_curso)
        db.session.commit()
        flash('Curso añadido correctamente!')
        return redirect(url_for('cursos.home'))

@cursos.route('/cursos/delete/<idCurso>')
def delete(idCurso):
    curso = Curso.query.get(idCurso)
    db.session.delete(curso)
    db.session.commit()
    flash('Curso Borrado!')
    return redirect(url_for('cursos.home'))

#listado de alumnos por curso
@cursos.route('/cursos/listadoAlumnos/<curso_id>', methods=["GET", "POST"])
def listado_alumnos(curso_id):
    curso = Curso.query.get(curso_id)
    listado = Matricula.query.join(Curso, Matricula.curso_id == curso_id).join(Alumno, Matricula.alumno_id==Alumno.idAlumno).add_columns(Alumno.apellido, Alumno.nombre, Alumno.cuil)
    aula = Aula.query.get(curso.aula_id)
    # for i in listado:
    #     print(i)
    # print(listado.count())
    return render_template('/cursos/listAlumnos.html', listado=listado, curso=curso, cantidad=math.trunc(listado.count()/3), capacidad = aula.capacidad)
    