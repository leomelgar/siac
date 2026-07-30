from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import date
from sqlalchemy import and_
from models.colege import db, Matricula, Alumno, Colegio

matricula_bp = Blueprint('matricula', __name__, url_prefix='/matriculas')

@matricula_bp.before_request
@login_required
def requerir_login():
    pass

TIPOS_INGRESO = [
    "Ingreso desde primaria",
    "Pase de otro establecimiento"
]


def _obtener_colegio_unico():
    """Devuelve el único colegio cargado en el sistema."""
    colegio = Colegio.query.first()
    if not colegio:
        raise Exception("No hay ningún colegio cargado en el sistema. Debe existir al menos uno.")
    return colegio


# -------------------------------------------------
# LISTADO CON FILTROS + PAGINACIÓN
# -------------------------------------------------
@matricula_bp.route('/')
def listar():
    periodo = request.args.get('periodo', type=int)
    estado = request.args.get('estado', type=str)
    tipo_ingreso = request.args.get('tipo_ingreso', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = 15

    query = Matricula.query

    if periodo:
        query = query.filter(Matricula.periodo_lectivo == periodo)
    if estado:
        query = query.filter(Matricula.estado_matricula == estado)
    if tipo_ingreso:
        query = query.filter(Matricula.tipo_ingreso == tipo_ingreso)

    pagination = query.order_by(
        Matricula.periodo_lectivo.desc(),
        Matricula.id_matricula.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    matriculas = pagination.items

    periodos = [p[0] for p in db.session.query(Matricula.periodo_lectivo)
                .distinct().order_by(Matricula.periodo_lectivo.desc()).all()]

    colegio = _obtener_colegio_unico()

    return render_template(
        'matricula/listar.html',
        matriculas=matriculas,
        pagination=pagination,
        periodos=periodos,
        tipos_ingreso=TIPOS_INGRESO,
        colegio=colegio,
        filtro_periodo=periodo,
        filtro_estado=estado,
        filtro_tipo_ingreso=tipo_ingreso
    )


# -------------------------------------------------
# NUEVA MATRÍCULA
# -------------------------------------------------
@matricula_bp.route('/nueva', methods=['GET', 'POST'])
def nueva_matricula():
    colegio = _obtener_colegio_unico()

    # id_alumno opcional (viene desde detalle de alumno o desde el form)
    id_alumno_preseleccionado = request.args.get('id_alumno', type=int)
    alumno_preseleccionado = None

    if id_alumno_preseleccionado:
        alumno_preseleccionado = Alumno.query.get(id_alumno_preseleccionado)

    if request.method == 'POST':
        try:
            id_alumno = int(request.form['id_alumno'])
            fecha_inscripcion = date.fromisoformat(request.form['fecha_inscripcion'])
            grado_nivel = request.form['grado_nivel'].strip()
            periodo_lectivo = int(request.form['periodo_lectivo'])
            tipo_ingreso = request.form.get('tipo_ingreso', '').strip()
            estado_matricula = request.form.get('estado_matricula', 'Activo')

            # Para no perder el alumno si hay error de validación
            alumno_preseleccionado = Alumno.query.get(id_alumno)

            if not grado_nivel:
                flash('El grado/nivel es obligatorio.', 'danger')
                return render_template('matricula/form.html',
                                       colegio=colegio,
                                       tipos_ingreso=TIPOS_INGRESO,
                                       matricula=None,
                                       alumno_preseleccionado=alumno_preseleccionado,
                                       fecha_hoy=date.today().isoformat())

            if tipo_ingreso not in TIPOS_INGRESO:
                flash('Debe seleccionar un tipo de ingreso válido.', 'danger')
                return render_template('matricula/form.html',
                                       colegio=colegio,
                                       tipos_ingreso=TIPOS_INGRESO,
                                       matricula=None,
                                       alumno_preseleccionado=alumno_preseleccionado,
                                       fecha_hoy=date.today().isoformat())

            if _existe_matricula(id_alumno, periodo_lectivo):
                flash('El alumno ya tiene una matrícula registrada para ese período lectivo.', 'warning')
                return render_template('matricula/form.html',
                                       colegio=colegio,
                                       tipos_ingreso=TIPOS_INGRESO,
                                       matricula=None,
                                       alumno_preseleccionado=alumno_preseleccionado,
                                       fecha_hoy=date.today().isoformat())

            nueva = Matricula(
                id_alumno=id_alumno,
                id_colegio=colegio.id_colegio,
                fecha_inscripcion=fecha_inscripcion,
                grado_nivel=grado_nivel,
                periodo_lectivo=periodo_lectivo,
                tipo_ingreso=tipo_ingreso,
                estado_matricula=estado_matricula
            )
            db.session.add(nueva)
            db.session.commit()
            flash('Matrícula registrada correctamente.', 'success')

            # Opcional: volver al detalle del alumno en lugar del listado
            # return redirect(url_for('alumno.detalle', id=id_alumno))
            return redirect(url_for('matricula.listar'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar la matrícula: {str(e)}', 'danger')

    return render_template(
        'matricula/form.html',
        colegio=colegio,
        tipos_ingreso=TIPOS_INGRESO,
        matricula=None,
        alumno_preseleccionado=alumno_preseleccionado,
        fecha_hoy=date.today().isoformat()
    )


# -------------------------------------------------
# EDITAR MATRÍCULA
# -------------------------------------------------
@matricula_bp.route('/<int:id_matricula>/editar', methods=['GET', 'POST'])
def editar_matricula(id_matricula):
    matricula = Matricula.query.get_or_404(id_matricula)
    alumnos = Alumno.query.order_by(Alumno.apellido, Alumno.nombre).all()
    colegio = _obtener_colegio_unico()

    if request.method == 'POST':
        try:
            id_alumno = int(request.form['id_alumno'])
            fecha_inscripcion = date.fromisoformat(request.form['fecha_inscripcion'])
            grado_nivel = request.form['grado_nivel'].strip()
            periodo_lectivo = int(request.form['periodo_lectivo'])
            tipo_ingreso = request.form.get('tipo_ingreso', '').strip()
            estado_matricula = request.form.get('estado_matricula', 'Activo')

            if not grado_nivel:
                flash('El grado/nivel es obligatorio.', 'danger')
                return render_template('matricula/form.html',
                                       alumnos=alumnos, colegio=colegio,
                                       tipos_ingreso=TIPOS_INGRESO,
                                       matricula=matricula)

            if tipo_ingreso not in TIPOS_INGRESO:
                flash('Debe seleccionar un tipo de ingreso válido.', 'danger')
                return render_template('matricula/form.html',
                                       alumnos=alumnos, colegio=colegio,
                                       tipos_ingreso=TIPOS_INGRESO,
                                       matricula=matricula)

            if _existe_matricula(id_alumno, periodo_lectivo, excluir_id=id_matricula):
                flash('El alumno ya tiene otra matrícula registrada para ese período lectivo.', 'warning')
                return render_template('matricula/form.html',
                                       alumnos=alumnos, colegio=colegio,
                                       tipos_ingreso=TIPOS_INGRESO,
                                       matricula=matricula)

            matricula.id_alumno = id_alumno
            matricula.id_colegio = colegio.id_colegio   # siempre el único colegio
            matricula.fecha_inscripcion = fecha_inscripcion
            matricula.grado_nivel = grado_nivel
            matricula.periodo_lectivo = periodo_lectivo
            matricula.tipo_ingreso = tipo_ingreso
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
        colegio=colegio,
        tipos_ingreso=TIPOS_INGRESO,
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
def _existe_matricula(id_alumno, periodo_lectivo, excluir_id=None):
    query = Matricula.query.filter(
        and_(
            Matricula.id_alumno == id_alumno,
            Matricula.periodo_lectivo == periodo_lectivo
        )
    )
    if excluir_id:
        query = query.filter(Matricula.id_matricula != excluir_id)
    return query.first() is not None

#--------------------------------------------------------
# Buscador
#------------------------------------------------------
@matricula_bp.route('/buscar-alumno')
def buscar_alumno():
    """Busca alumnos por apellido o legajo (AJAX)."""
    q = request.args.get('q', '').strip()

    if len(q) < 2:
        return {'alumnos': []}

    # Busca por apellido O por legajo
    alumnos = Alumno.query.filter(
        db.or_(
            Alumno.apellido.ilike(f'%{q}%'),
            Alumno.legajo.ilike(f'%{q}%'),      # o Alumno.dni.ilike(f'%{q}%')
            Alumno.cuil.ilike(f'%{q}%')
        )
    ).order_by(Alumno.apellido, Alumno.nombre).limit(15).all()

    resultado = [
        {
            'id': a.id,
            'apellido': a.apellido,
            'nombre': a.nombre,
            'cuil':a.cuil,
            'legajo': a.legajo,                # o a.dni
            'texto': f"{a.apellido}, {a.nombre} — Legajo: {a.legajo}"
        }
        for a in alumnos
    ]
    return {'alumnos': resultado}