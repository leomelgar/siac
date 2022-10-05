from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.colege import Docente, Asignatura, Catedra
from utils.db import db

catedras = Blueprint("catedras", __name__)

@catedras.route('/catedras/nueva', methods=["POST","GET"])
def new_catedra():
    docentes=Docente.query.all()
    asignaturas=Asignatura.query.all()
    return render_template('/catedras/nueva', docentes=docentes, asignaturas=asignaturas)