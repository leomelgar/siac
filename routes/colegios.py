from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.colege import Colegio
from utils.db import db

colegios = Blueprint("colegios", __name__)

@colegios.route('/colegios/home')
def home():
    colegios = Colegio.query.all()
    return render_template('/colegios/home.html', colegios=colegios)

@colegios.route('/newColegio', methods=['POST'])
def add_colegio():
    if request.method == 'POST':
    #recibo los datos del formulario
        nombre = request.form['nombre']
        direccion = request.form['direccion']
        telefono  = request.form['telefono']
        email = request.form['email']
        #creo un nuevo objeto colegio
        new_colegio = Colegio(nombre, direccion, telefono, email)
        #guardo el nuevo objeto en la base de datos
        db.session.add(new_colegio)
        db.session.commit()
        flash('Colegio añadido!')
        return redirect(url_for('colegios.home'))

@colegios.route('/updatecolegio/<idColegios>', methods=["GET","POST"])
def updateColegio(idColegios):
    colegio = Colegio.query.get(idColegios)
    if request.method == "POST":
        colegio.nombre = request.form['nombre']
        colegio.direccion = request.form['direccion']
        colegio.telefono = request.form['telefono']
        colegio.email = request.form['email']
        db.session.commit()
        flash('Datos Actualizados exitosamente!')
        return redirect(url_for('colegios.home'))
    return render_template("/colegios/updateColegio.html", colegio=colegio)

@colegios.route("/deleteColegio/<idColegios>", methods=['GET'])
def deleteColegio(idColegios):
    colegio = Colegio.query.get(idColegios)
    db.session.delete(colegio)
    db.session.commit()
    flash("Colegio eliminado!")
    return redirect(url_for('colegios.home'))
