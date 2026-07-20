from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models.colege import Asignatura
from utils.db import db


asignaturas = Blueprint("asignaturas", __name__)

@asignaturas.route("/asignaturas/list")
def list():
    asignaturas = Asignatura.query.all()
    # 2. Convertimos la lista de objetos a una lista de diccionarios
    lista_asignaturas = [asignatura.to_dict() for asignatura in asignaturas]
    return render_template("/asignaturas/list.html", asignaturas=lista_asignaturas)

@asignaturas.route("/asignaturas/new", methods=["POST"])
def new():
    if request.method == 'POST':
        nombre = request.form['nombre_asignatura']
        descripcion = request.form['descripcion']
        creditos = request.form['creditos']

        new_asignatura = Asignatura(id_colegio=1, nombre_asignatura=nombre, descripcion=descripcion, creditos=creditos)
        db.session.add(new_asignatura)
        db.session.commit()
        flash('Asignatura agregada!')
        return redirect(url_for('asignaturas.list'))

@asignaturas.route("/asignaturas/update/<id_asignatura>", methods=["POST","GET"])
def update(id_asignatura):
    asignatura = Asignatura.query.get(id_asignatura)
    if request.method == "POST":
        asignatura.nombre_asignatura = request.form['nombre_asignatura']
        asignatura.descripcion = request.form['descripcion']
        asignatura.creditos = request.form['creditos']
        db.session.commit()
        flash('Asignatura actualizada!')
        return redirect(url_for('asignaturas.list'))
    return render_template("/asignaturas/update.html", asignatura=asignatura)

@asignaturas.route("/asignaturas/delete/<id_asignatura>")
def delete(id_asignatura):
    asignatura = Asignatura.query.get(id_asignatura)
    db.session.delete(asignatura)
    db.session.commit()
    flash('Asignatura Borrada correctamente!')
    return redirect(url_for('asignaturas.list'))