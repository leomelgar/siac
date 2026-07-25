from crypt import methods
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.colege import Aula, Colegio
from utils.db import db

aulas = Blueprint("aulas", __name__)

@aulas.route('/aulas/home')
def home():
    aulas = Aula.query.all()
    return render_template('/aulas/home.html', aulas=aulas)



@aulas.route('/new', methods=["POST"])
def new_aula():
    if request.method=="POST":
        nombre_aula = request.form['nombre_aula']
        capacidad = request.form['capacidad']
        ubicacion = request.form['ubicacion']
        id_colegio =1
        new_aula = Aula(id_colegio,nombre_aula, capacidad, ubicacion)
        db.session.add(new_aula)
        db.session.commit()
        flash('Aula creada correctamente!')
        return redirect(url_for('aulas.home'))

@aulas.route('/cursos/delete/<id_aula>')
def delete(id_aula):
    aula = Aula.query.get(id_aula)
    db.session.delete(aula)
    db.session.commit()
    flash('Aula Borrada!')
    return redirect(url_for('aulas.home'))