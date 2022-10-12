from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.colege import Asignatura
from utils.db import db

asignaturas = Blueprint("asignaturas", __name__)

@asignaturas.route("/asignaturas/list")
def list():
    asignaturas = Asignatura.query.all()
    return render_template("/asignaturas/list.html", asignaturas=asignaturas)

@asignaturas.route("/asignaturas/new", methods=["POST"])
def new():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']

        new_asignatura = Asignatura(nombre, descripcion)
        db.session.add(new_asignatura)
        db.session.commit()
        flash('Asignatura agregada!')
        return redirect(url_for('asignaturas.list'))
