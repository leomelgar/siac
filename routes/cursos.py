from crypt import methods
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.colege import Curso, Catedra, Aula, Turno, Matricula, Horario
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
    matriculas = Matricula.query.all()
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