from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import date
from sqlalchemy import and_
from models.colege import db, Matricula, Alumno, Colegio

matricula_bp = Blueprint('matricula', __name__, url_prefix='/matriculas')


# -------------------------------------------------
# LISTADO CON FILTROS
# -------------------------------------------------
@matricula_bp.route('/')
def listar():
    # Parámetros de filtro
    periodo = request.args.get('periodo', type=int)
    id_colegio = request.args.get('id_colegio', type=int)
    estado = request.args.get('estado', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = 15          # Cantidad de registros por página (ajustable)

    query = Matricula.query

    if periodo:
        query = query.filter(Matricula.periodo_lectivo == periodo)
    if id_colegio:
        query = query.filter(Matricula.id_colegio == id_colegio)
    if estado:
        query = query.filter(Matricula.estado_matricula == estado)

    # Orden + paginación
    pagination = query.order_by(
        Matricula.periodo_lectivo.desc(),
        Matricula.id_matricula.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    matriculas = pagination.items

    # Datos para los selects de filtro
    periodos = db.session.query(Matricula.periodo_lectivo)\
                         .distinct()\
                         .order_by(Matricula.periodo_lectivo.desc())\
                         .all()
    periodos = [p[0] for p in periodos]

    colegios = Colegio.query.order_by(Colegio.nombre_colegio).all()

    return render_template(
        'matricula/listar.html',
        matriculas=matriculas,
        pagination=pagination,
        periodos=periodos,
        colegios=colegios,
        filtro_periodo=periodo,
        filtro_colegio=id_colegio,
        filtro_estado=estado
    )


# -------------------------------------------------
# NUEVA MATRÍCULA
# -------------------------------------------------
@matricula_bp.route('/nueva', methods=['GET', 'POST'])
def nueva_matricula():
    alumnos = Alumno.query.order_by(Alumno.apellido, Alumno.nombre).all()
    colegios = Colegio.query.order_by(Colegio.nombre_colegio).all()

    if request.method == 'POST':
        try:
            id_alumno = int(request.form['id_alumno'])
            id_colegio = int(request.form['id_colegio'])
            fecha_inscripcion = date.fromisoformat(request.form['fecha_inscripcion'])
            grado_nivel = request.form['grado_nivel'].strip()
            periodo_lectivo = int(request.form['periodo_lectivo'])
            estado_matricula = request.form.get('estado_matricula', 'Activo')

            if not grado_nivel:
                flash('El grado/nivel es obligatorio.', 'danger')
                return render_template('matricula/form.html',
                                       alumnos=alumnos, colegios=colegios,
                                       matricula=None, fecha_hoy=date.today().isoformat())

            # Validación de unicidad
            if _existe_matricula(id_alumno, id_colegio, periodo_lectivo):
                flash('Ya existe una matrícula de este alumno en el mismo colegio y período lectivo.', 'warning')
                return render_template('matricula/form.html',
                                       alumnos=alumnos, colegios=colegios,
                                       matricula=None, fecha_hoy=date.today().isoformat())

            nueva = Matricula(
                id_alumno=id_alumno,
                id_colegio=id_colegio,
                fecha_inscripcion=fecha_inscripcion,
                grado_nivel=grado_nivel,
                periodo_lectivo=periodo_lectivo,
                estado_matricula=estado_matricula
            )
            db.session.add(nueva)
            db.session.commit()
            flash('Matrícula registrada correctamente.', 'success')
            return redirect(url_for('matricula.listar'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar la matrícula: {str(e)}', 'danger')

    return render_template(
        'matricula/form.html',
        alumnos=alumnos,
        colegios=colegios,
        matricula=None,
        fecha_hoy=date.today().isoformat()
    )


# -------------------------------------------------
# EDITAR MATRÍCULA
# -------------------------------------------------
@matricula_bp.route('/<int:id_matricula>/editar', methods=['GET', 'POST'])
def editar_matricula(id_matricula):
    matricula = Matricula.query.get_or_404(id_matricula)
    alumnos = Alumno.query.order_by(Alumno.apellido, Alumno.nombre).all()
    colegios = Colegio.query.order_by(Colegio.nombre_colegio).all()

    if request.method == 'POST':
        try:
            id_alumno = int(request.form['id_alumno'])
            id_colegio = int(request.form['id_colegio'])
            fecha_inscripcion = date.fromisoformat(request.form['fecha_inscripcion'])
            grado_nivel = request.form['grado_nivel'].strip()
            periodo_lectivo = int(request.form['periodo_lectivo'])
            estado_matricula = request.form.get('estado_matricula', 'Activo')

            if not grado_nivel:
                flash('El grado/nivel es obligatorio.', 'danger')
                return render_template('matricula/form.html',
                                       alumnos=alumnos, colegios=colegios,
                                       matricula=matricula)

            # Validación de unicidad (excluyendo la matrícula actual)
            if _existe_matricula(id_alumno, id_colegio, periodo_lectivo, excluir_id=id_matricula):
                flash('Ya existe otra matrícula de este alumno en el mismo colegio y período lectivo.', 'warning')
                return render_template('matricula/form.html',
                                       alumnos=alumnos, colegios=colegios,
                                       matricula=matricula)

            # Actualizar campos
            matricula.id_alumno = id_alumno
            matricula.id_colegio = id_colegio
            matricula.fecha_inscripcion = fecha_inscripcion
            matricula.grado_nivel = grado_nivel
            matricula.periodo_lectivo = periodo_lectivo
            matricula.estado_matricula = estado_matricula

            db.session.commit()
            flash('Matrícula actualizada correctamente.', 'success')
            return redirect(url_for('matricula.listar'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la matrícula: {str(e)}', 'danger')

    return render_template(
        'matricula/form.html',
        alumnos=alumnos,
        colegios=colegios,
        matricula=matricula
    )


# -------------------------------------------------
# DAR DE BAJA
# -------------------------------------------------
@matricula_bp.route('/<int:id_matricula>/baja', methods=['POST'])
def dar_baja(id_matricula):
    matricula = Matricula.query.get_or_404(id_matricula)
    matricula.estado_matricula = 'Baja'
    db.session.commit()
    flash('Matrícula dada de baja.', 'info')
    return redirect(url_for('matricula.listar'))


# -------------------------------------------------
# FUNCIÓN AUXILIAR DE UNICIDAD
# -------------------------------------------------
def _existe_matricula(id_alumno, id_colegio, periodo_lectivo, excluir_id=None):
    """
    Verifica si ya existe una matrícula con la misma combinación
    alumno + colegio + período.
    Si se pasa excluir_id, se ignora esa matrícula (útil en edición).
    """
    query = Matricula.query.filter(
        and_(
            Matricula.id_alumno == id_alumno,
            Matricula.id_colegio == id_colegio,
            Matricula.periodo_lectivo == periodo_lectivo
        )
    )
    if excluir_id:
        query = query.filter(Matricula.id_matricula != excluir_id)

    return query.first() is not None