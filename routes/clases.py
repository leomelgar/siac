from crypt import methods
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.colege import Clase, Curso, Catedra, Horario, Docente
from utils.db import db

clases = Blueprint("clases", __name__)

@clases.route('/clases/home')
def home():
    #clases = Clase.query.all()
    clases = Clase.query.join(Catedra, Clase.catedra_id==Catedra.idCatedra).join(Curso, Clase.curso_id==Curso.idCurso).join(Horario, Clase.horario_id==Horario.idHorario).add_columns(Clase.idClase, Clase.nombre_clase, Catedra.nombre_cat, Curso.curso, Curso.division, Horario.dia, Horario.descripcion)
    return render_template('/clases/home.html', clases=clases)

@clases.route('/clases/nuevaClase', methods=["POST","GET"])
def nueva_clase():
    cursos = Curso.query.all()
    catedras = Catedra.query.all()
    catedras = Catedra.query.join(Docente, Catedra.docente_id==Docente.idDocente).add_columns(Catedra.idCatedra, Catedra.nombre_cat, Docente.apellido, Docente.nombre)
    horarios = Horario.query.all()
    if request.method == "POST" and 'tag' in request.form:
        tag = request.form['tag']
        search = "%{}%".format(tag)
        catedras = Catedra.query.filter(Catedra.nombre_cat.like(search)).join(Docente, Catedra.docente_id==Docente.idDocente).add_columns(Catedra.nombre_cat, Docente.apellido, Docente.nombre)
        if not catedras:
            flash('No existe registro que coincidan')
        else:
            return render_template('/clases/nuevaClase.html', catedras=catedras, cursos=cursos, horarios=horarios)
    return render_template('/clases/nuevaClase.html', catedras=catedras, cursos=cursos, horarios=horarios)

@clases.route('/clases/add_clase', methods=["POST"])
def add_clase():
    if request.method=="POST":
        nombre_clase = request.form['nombre_clase']
        curso_id = request.form['curso_id']
        catedra_id = request.form['catedra_id']
        horario_id = request.form['horario_id']
        
        new_clase = Clase(nombre_clase,curso_id,catedra_id,horario_id)
        db.session.add(new_clase)
        db.session.commit()
        flash('Clase añadido correctamente!')
        return redirect(url_for('clases.home'))

@clases.route('/clases/delete/<idClase>')
def delete(idClase):
    clase = Clase.query.get(idClase)
    db.session.delete(clase)
    db.session.commit()
    flash('Clase Borrada!')
    return redirect(url_for('clases.home'))