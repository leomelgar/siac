from crypt import methods
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.colege import Aula, Colegio
from utils.db import db

aulas = Blueprint("aulas", __name__)

@aulas.route('/aulas/home')
def home():
    aulas = Aula.query.all()
    return render_template('/aulas/home.html', aulas=aulas)

@aulas.route('/aulas/nuevo', methods=["POST","GET"])
def new():
    aulas = Aula.query.all()
    return render_template('/aulas/new.html', aulas=aulas)

@aulas.route('/aulas/add_aula', methods=["POST"])
def add_aula():
    if request.method=="POST":
        nombre_curso = request.form['nombre_curso']
        division = request.form['division']
        periodo = request.form['periodo']
        aula_id = request.form['aula_id']
        turno_id = request.form['turno_id']
       
        #new_curso = Curso(nombre_curso, division, periodo, aula_id, turno_id)
        #db.session.add(new_curso)
        #db.session.commit()
        flash('Curso añadido correctamente!')
        return redirect(url_for('cursos.home'))

@aulas.route('/cursos/delete/<id_aula>')
def delete(id_aula):
    aula = Aula.query.get(id_aula)
    db.session.delete(aula)
    db.session.commit()
    flash('Aula Borrada!')
    return redirect(url_for('aulas.home'))