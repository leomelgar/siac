from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.colege import Tutor
from utils.db import db

tutores = Blueprint("tutores", __name__)

@tutores.route('/tutores/home')
def home():
    tutores = Tutor.query.all()
    return render_template('/tutores/home.html', tutores=tutores)

@tutores.route('/newTutor', methods=['POST'])
def new_tutor():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        dni = request.form['dni']
        telefono  = request.form['telefono']
        email = request.form['email']
        direccion = request.form['direccion']
        parentesco = request.form['parentesco']
        legal = request.form['legal']
    

        new_tutor = Tutor(nombre, apellido, dni, telefono, email, direccion, parentesco, legal)
        db.session.add(new_tutor)
        db.session.commit()
        flash('Tutor añadido correctamente!')
        return redirect(url_for('tutores.home'))

@tutores.route('/tutores/view/<id_tutor>', methods=['GET'])
def view(id_tutor):
    tutor = Tutor.query.get(id_tutor)
    return render_template('/tutores/view.html', tutor=tutor)

@tutores.route("/updateTutor/<id_tutor>", methods=['POST', 'GET'])
def updateTutor(id_tutor):
    tutor = Tutor.query.get(id_tutor)
    if request.method == "POST":
      tutor.nombre = request.form['nombre']
      tutor.apellido = request.form['apellido']
      tutor.cuil = request.form['cuil']
      tutor.direccion = request.form['direccion']
      tutor.telefono  = request.form['telefono']
      tutor.email = request.form['email']
      db.session.commit()
      flash('Datos Actualizados!')
      return redirect(url_for('tutores.home'))
    return render_template("/tutores/updateTutor.html", tutor=tutor)

@tutores.route("/deleteTutor/<id_tutor>", methods=["GET"])
def deleteTutor(id_tutor):
    tutor = Tutor.query.get(id_tutor)
    db.session.delete(tutor)
    db.session.commit()
    flash('Tutor Borrado!')
    return redirect(url_for('tutores.home'))
