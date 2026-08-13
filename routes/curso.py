# ==========================================
# BLUEPRINT: GESTIÓN DE CURSOS
# ==========================================
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from utils.db import db
from models.colege import Curso, Colegio, Matricula, Clase, Alumno

curso_bp = Blueprint('curso', __name__, url_prefix='/cursos')


# ------------------------------------------
# LISTAR CURSOS (filtrable por colegio y período)
# ------------------------------------------
@curso_bp.route('/', methods=['GET'])
@login_required
def listar():
    id_colegio = request.args.get('id_colegio', type=int)
    periodo = request.args.get('periodo', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = 15

    query = (
        Curso.query
        .options(
            joinedload(Curso.clases).joinedload(Clase.aula)
        )
    )

    if id_colegio:
        query = query.filter_by(id_colegio=id_colegio)
    if periodo:
        query = query.filter_by(periodo_lectivo=periodo)

    pagination = query.order_by(
        Curso.periodo_lectivo.desc(),
        Curso.anio,
        Curso.division
    ).paginate(page=page, per_page=per_page, error_out=False)

    cursos = pagination.items
    colegios = Colegio.query.order_by(Colegio.nombre_colegio).all()
    
    return render_template(
        'cursos/listar.html',
        cursos=cursos,
        colegios=colegios,
        id_colegio=id_colegio,
        periodo=periodo,
        pagination=pagination
    )


# ------------------------------------------
# CREAR CURSO
# ------------------------------------------
@curso_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def crear():
    colegios = Colegio.query.order_by(Colegio.nombre_colegio).all()

    if request.method == 'POST':
        curso = Curso(
            id_colegio=request.form.get('id_colegio', type=int),
            anio=request.form.get('anio'),
            division=request.form.get('division'),
            periodo_lectivo=request.form.get('periodo_lectivo', type=int),
            turno_preferente=request.form.get('turno_preferente') or None
        )
        db.session.add(curso)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('Ya existe un curso con ese año, división y período para este colegio.', 'danger')
            return render_template('cursos/form.html', colegios=colegios, curso=None, form=request.form)

        flash('Curso creado correctamente.', 'success')
        return redirect(url_for('curso.detalle', id_curso=curso.id_curso))

    return render_template('cursos/form.html', colegios=colegios, curso=None, form=None)


# ------------------------------------------
# EDITAR CURSO
# ------------------------------------------
@curso_bp.route('/<int:id_curso>/editar', methods=['GET', 'POST'])
@login_required
def editar(id_curso):
    curso = Curso.query.get_or_404(id_curso)
    colegios = Colegio.query.order_by(Colegio.nombre_colegio).all()

    if request.method == 'POST':
        curso.id_colegio = request.form.get('id_colegio', type=int)
        curso.anio = request.form.get('anio')
        curso.division = request.form.get('division')
        curso.periodo_lectivo = request.form.get('periodo_lectivo', type=int)
        curso.turno_preferente = request.form.get('turno_preferente') or None

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('Ya existe un curso con ese año, división y período para este colegio.', 'danger')
            return render_template('cursos/form.html', colegios=colegios, curso=curso, form=request.form)

        flash('Curso actualizado correctamente.', 'success')
        return redirect(url_for('curso.detalle', id_curso=curso.id_curso))

    return render_template('cursos/form.html', colegios=colegios, curso=curso, form=None)


# ------------------------------------------
# DETALLE DE CURSO (alumnos matriculados + clases dictadas)
# ------------------------------------------
@curso_bp.route('/<int:id_curso>', methods=['GET'])
@login_required
def detalle(id_curso):
    curso = Curso.query.get_or_404(id_curso)
    matriculas = (
        Matricula.query
        .filter_by(id_curso=id_curso)
        .join(Alumno, Matricula.id_alumno == Alumno.id)
        .order_by(Alumno.apellido, Alumno.nombre)
        .all()
    )
    clases = Clase.query.filter_by(id_curso=id_curso).all()

    return render_template(
        'cursos/detalle.html',
        curso=curso,
        matriculas=matriculas,
        clases=clases
    )


# ------------------------------------------
# ELIMINAR CURSO
# ------------------------------------------
@curso_bp.route('/<int:id_curso>/eliminar', methods=['POST'])
@login_required
def eliminar(id_curso):
    curso = Curso.query.get_or_404(id_curso)

    if curso.matriculas or curso.clases:
        flash('No se puede eliminar: el curso tiene alumnos matriculados o clases asociadas.', 'danger')
        return redirect(url_for('curso.detalle', id_curso=id_curso))

    db.session.delete(curso)
    db.session.commit()
    flash('Curso eliminado.', 'success')
    return redirect(url_for('curso.listar'))


# ------------------------------------------
# ALTA MASIVA: buscar alumnos sin curso asignado en el mismo
# colegio + período lectivo, por apellido/nombre o legajo
# ------------------------------------------
@curso_bp.route('/<int:id_curso>/matricular-masivo', methods=['GET'])
@login_required
def matricular_masivo_form(id_curso):
    curso = Curso.query.get_or_404(id_curso)
    q = request.args.get('q', '').strip()

    query = (
        Matricula.query
        .join(Alumno, Matricula.id_alumno == Alumno.id)
        .filter(
            Matricula.id_colegio == curso.id_colegio,
            Matricula.periodo_lectivo == curso.periodo_lectivo,
            Matricula.id_curso.is_(None)
        )
    )

    if q:
        like = f'%{q}%'
        query = query.filter(
            db.or_(
                Alumno.apellido.ilike(like),
                Alumno.nombre.ilike(like),
                Alumno.legajo.ilike(like)
            )
        )

    matriculas_disponibles = query.order_by(Alumno.apellido, Alumno.nombre).all()

    return render_template(
        'cursos/matricularMasivo.html',
        curso=curso,
        matriculas=matriculas_disponibles,
        q=q
    )


@curso_bp.route('/<int:id_curso>/matricular-masivo', methods=['POST'])
@login_required
def matricular_masivo(id_curso):
    curso = Curso.query.get_or_404(id_curso)
    ids = request.form.getlist('id_matricula')
    q = request.form.get('q', '')

    if not ids:
        flash('No se seleccionó ningún alumno.', 'warning')
        return redirect(url_for('curso.matricular_masivo_form', id_curso=id_curso, q=q))

    actualizadas = (
        Matricula.query
        .filter(
            Matricula.id_matricula.in_(ids),
            Matricula.id_colegio == curso.id_colegio,
            Matricula.periodo_lectivo == curso.periodo_lectivo
        )
        .update({Matricula.id_curso: curso.id_curso}, synchronize_session=False)
    )
    db.session.commit()

    flash(f'{actualizadas} alumno(s) asignado(s) al curso.', 'success')
    return redirect(url_for('curso.detalle', id_curso=id_curso))


# ------------------------------------------
# DESVINCULAR UNA MATRÍCULA DEL CURSO
# ------------------------------------------
@curso_bp.route('/<int:id_curso>/desmatricular/<int:id_matricula>', methods=['POST'])
@login_required
def desmatricular(id_curso, id_matricula):
    matricula = Matricula.query.get_or_404(id_matricula)
    if matricula.id_curso == id_curso:
        matricula.id_curso = None
        db.session.commit()
        flash('Alumno desvinculado del curso.', 'success')

    return redirect(url_for('curso.detalle', id_curso=id_curso))