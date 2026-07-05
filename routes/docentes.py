from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.colege import Docente, Colegio, Asignatura, Persona
from utils.db import db

docentes = Blueprint("docentes", __name__)

@docentes.route('/docentes/home')
def home():
    #docentes = db.session.query(Docente).join(Persona).filter(Persona.id==Docente.id).all()
    #docentes = Docente.query.join(Persona).filter(Persona.id==Docente.id).all()
    docentes = Persona.query.filter(Persona.tipo_persona=="docente").all()
    #docentes = Docente.query.all()
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
        cuil = request.form['dni']

        new_docente = Docente(nombre, apellido, dni, fecha_nac, id_colegio, cuil, cargo, fecha_contratacion, estado_contractual, direccion, telefono, email)
        db.session.add(new_docente)
        db.session.commit()
        flash('Docente añadido correctamente!')
        return redirect(url_for('docentes.home'))

@docentes.route('/docentes/view/<id_docente>', methods=['GET'])
def view(id_docente):
    docente = Docente.query.get(id_docente)
    return render_template('/docentes/view.html', docente=docente)

@docentes.route("/updateDocente/<id>", methods=['POST', 'GET'])
def updateDocente(id):
    docente = Docente.query.get(id)
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

@docentes.route("/deleteDocente/<id>", methods=["GET"])
def deleteDocente(id):
    docente = Docente.query.get(id)
    db.session.delete(docente)
    db.session.commit()
    flash('Docente Borrado!')
    return redirect(url_for('docentes.home'))
