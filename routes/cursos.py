from crypt import methods
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.colege import Curso, Catedra, Aula, Docente, Turno, Matricula, Horario
from utils.db import db

cursos = Blueprint("cursos", __name__)

@cursos.route('/cursos/home')
def home():
    cursos = Curso.query.all()
    return render_template('/cursos/home.html', cursos=cursos)

@cursos.route('/cursos/nuevo', methods=["POST","GET"])
def new():
    catedras = Catedra.query.all()
    aulas = Aula.query.all()
    turnos = Turno.query.all()
    horarios = Horario.query.all()
    if request.method == "POST" and 'tag' in request.form:
        tag = request.form['tag']
        search = "%{}%".format(tag)
        catedras = Catedra.query.filter(Catedra.nombre.like(search))
        if not catedras:
            flash("No existe registro...")
        else:
            return render_template('/cursos/curso.html', catedras=catedras, aulas=aulas, turnos=turnos, horarios=horarios)
    return render_template('/cursos/curso.html', catedras=catedras, aulas=aulas, turnos=turnos, horarios=horarios)

@cursos.route('/cursos/add_curso', methods=["POST"])
def add_curso():
    if request.method=="POST":
        nombre = request.form['nombre']
        division = request.form['division']
        aula_id = request.form['aula_id']
        turno_id = request.form['turno_id']
        horario_id = request.form['horario_id']

        new_curso = Curso(nombre,division,aula_id,turno_id,horario_id)
        db.session.add(new_curso)
        db.session.commit()
        flash('Curso añadido correctamente!')
        return redirect(url_for('cursos.home'))