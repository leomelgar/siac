from crypt import methods
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.colege import Docente, Asignatura, Catedra
from utils.db import db

catedras = Blueprint("catedras", __name__)

@catedras.route('/catedras/nueva', methods=["POST","GET"])
def catedra():
    docentes=Docente.query.all()
    asignaturas=Asignatura.query.all()
    if request.method == "POST" and 'tag' in request.form:
        tag = request.form['tag']
        search = "%{}%".format(tag)
        docentes = Docente.query.filter(Docente.apellido.like(search))
        if not docentes:
            flash("No existe registro...")
        else:
            return render_template('/catedras/catedra.html', docentes=docentes, asignaturas=asignaturas)
    return render_template('/catedras/catedra.html', docentes=docentes, asignaturas=asignaturas)

@catedras.route('/catedras/new', methods=["POST"])
def new_catedra():
    if request.method == "POST":
        nombre = request.form["nombre"]
        cargaHoraria = request.form["cargaHoraria"]
        tipoCargo = request.form["tipoCargo"]
        caracter = request.form["caracter"]
        asignatura_id = request.form["asignatura_id"]
        docente_id = request.form["docente_id"]

        new_catedra = Catedra(nombre, cargaHoraria, tipoCargo, caracter, asignatura_id, docente_id)
        db.session.add(new_catedra)
        db.session.commit()
        docente = Docente.query.get(docente_id)
        asignatura = Asignatura.query.get(asignatura_id)
        flash('Catedra asignada correctamente!')
        return render_template('/catedras/view.html', catedra=new_catedra, docente=docente, asignatura=asignatura)

# @catedras.route('/catedras/view/<idCatedra>', methods=["POST"])
# def view(idCatedra):
#     catedra = Catedra.query.get(idCatedra)
#     return redirect(url_for())

