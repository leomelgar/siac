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
        cuil = request.form['cuil']
        direccion = request.form['direccion']
        telefono  = request.form['telefono']
        email = request.form['email']
        colegio_id = request.form['colegio_id']

        new_docente = Docente(nombre, apellido, cuil, direccion, telefono, email, colegio_id)
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
