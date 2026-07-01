from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.colege import Docente, Colegio, Asignatura
from utils.db import db

docentes = Blueprint("docentes", __name__)

@docentes.route('/docentes/home')
def home():
    docentes = Docente.query.all()
    colegios = Colegio.query.all()
    return render_template('/docentes/home.html', docentes=docentes, colegios=colegios)

@docentes.route('/newDocente', methods=['POST'])
def new_docente():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        dni = request.form['dni']
        fecha_nac = request.form['fecha_nac']
        direccion = request.form['direccion']
        cargo = request.form['cargo']
        telefono  = request.form['telefono']
        email = request.form['email']
        id_colegio = request.form['id_colegio']
        fecha_contratacion = request.form['fecha_contratacion']
        estado_contractual = request.form['estado_contractual']

        new_docente = Docente(id_colegio, nombre, apellido, dni, fecha_nac, direccion, cargo, email, telefono, fecha_contratacion, estado_contractual)
        db.session.add(new_docente)
        db.session.commit()
        flash('Docente añadido correctamente!')
        return redirect(url_for('docentes.home'))

@docentes.route("/updateDocente/<idDocente>", methods=['POST', 'GET'])
def updateDocente(idDocente):
    docente = Docente.query.get(idDocente)
    if request.method == "POST":
      docente.nombre = request.form['nombre']
      docente.apellido = request.form['apellido']
      docente.cuil = request.form['cuil']
      docente.direccion = request.form['direccion']
      docente.telefono  = request.form['telefono']
      docente.email = request.form['email']
      db.session.commit()
      flash('Datos Actualizados!')
      return redirect(url_for('docentes.home'))
    return render_template("/docentes/updateDocente.html", docente=docente)

@docentes.route("/deleteDocente/<idDocente>", methods=["GET"])
def deleteDocente(idDocente):
    docente = Docente.query.get(idDocente)
    db.session.delete(docente)
    db.session.commit()
    flash('Docente Borrado!')
    return redirect(url_for('docentes.home'))
