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

@aulas.route('/update/<id_aula>', methods=["POST"])
def update_aula(id_aula):
    aula = db.session.get(Aula, id_aula)
    if not aula:
            flash('Aula no existe.', 'error')
            return redirect(url_for('aulas.home')) # Mejor usar redirect aquí
    if request.method=="POST":
        try:
            aula.nombre_aula = request.form.get('nombre_aula') or aula.nombre_aula
            aula.capacidad = request.form.get('capacidad') or aula.capacidad
            aula.ubicacion = request.form.get('ubicacion') or aula.ubicacion
            db.session.commit()
            flash('¡Datos Actualizados con éxito!', 'success')
            # Patrón PRG: Redirigir en lugar de renderizar directamente tras un POST
            return redirect(url_for('aulas.home'))
        except ValueError:
                    db.session.rollback()
                    flash("El formato de fecha ingresado no es válido.", "danger")
                    return redirect(url_for('aulas.home'))
            # Método GET: Mostrar el formulario con los datos actuales
    return render_template("/aulas/home.html")

@aulas.route('/aulas/delete/<id_aula>')
def delete(id_aula):
    aula = Aula.query.get(id_aula)
    db.session.delete(aula)
    db.session.commit()
    flash('Aula Borrada!')
    return redirect(url_for('aulas.home'))