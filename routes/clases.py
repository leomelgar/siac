from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.colege import Clase, Curso, Catedra, Horario
from utils.db import db

clases = Blueprint("clases", __name__)

@clases.route('/clases/home')
def home():
    clases = Clase.query.all()
    return render_template('/clases/home.html', clases=clases)

@clases.route('/clases/nuevaClase', methods=["POST","GET"])
def nueva_clase():
    cursos = Curso.query.all()
    catedras = Catedra.query.all()
    horarios = Horario.query.all()
    if request.method == "POST" and 'tag' in request.form:
        tag = request.form['tag']
        search = "%{}%".format(tag)
        catedras = Catedra.query.filter(Catedra.nombre.like(search))
        if not catedras:
            flash('No existe registro que coincidan')
        else:
            return render_template('/clases/nuevaClase.html', catedras=catedras, cursos=cursos, horarios=horarios)
    return render_template('/clases/nuevaClase.html', catedras=catedras, cursos=cursos, horarios=horarios)