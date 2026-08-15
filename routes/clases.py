from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from utils.db import db
from utils.utils_matriculacion import vincular_clase_a_matriculas_del_curso
from models.colege import Clase, Asignatura, Docente, Aula, Turno, Horario, Curso

clases_bp = Blueprint('clases', __name__, url_prefix='/clases')

@clases_bp.before_request
@login_required
def requerir_login():
    pass

DIAS_SEMANA = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']


# ==========================================
# VALIDACIÓN DE SOLAPAMIENTO
# ==========================================
def verificar_solapamiento(id_aula, dia_semana, hora_desde, hora_hasta, ciclo_lectivo, excluir_horario_id=None):
    """
    Devuelve el registro Horario en conflicto (o None) si en la misma aula, mismo día
    y mismo ciclo lectivo ya existe una franja horaria que se superpone con la solicitada.

    Dos rangos [hora_desde, hora_hasta) se solapan si:
        horario.hora_desde < hora_hasta_nueva  AND  horario.hora_hasta > hora_desde_nueva
    """
    query = (
        db.session.query(Horario)
        .join(Clase, Horario.id_clase == Clase.id_clase)
        .filter(
            Clase.id_aula == id_aula,
            Clase.ciclo_lectivo == ciclo_lectivo,
            Horario.dia_semana == dia_semana,
            Horario.hora_desde < hora_hasta,
            Horario.hora_hasta > hora_desde,
        )
    )
    if excluir_horario_id:
        query = query.filter(Horario.id_horario != excluir_horario_id)
    return query.first()


# ==========================================
# LISTADO PAGINADO
# ==========================================
@clases_bp.route('/')
def listar():
    page = request.args.get('page', 1, type=int)
    per_page = 10

    ciclo = request.args.get('ciclo_lectivo', type=int)
    id_docente = request.args.get('id_docente', type=int)
    id_aula = request.args.get('id_aula', type=int)

    query = Clase.query

    if ciclo:
        query = query.filter(Clase.ciclo_lectivo == ciclo)
    if id_docente:
        query = query.filter(Clase.id_docente == id_docente)
    if id_aula:
        query = query.filter(Clase.id_aula == id_aula)

    paginacion = query.order_by(Clase.ciclo_lectivo.desc(), Clase.id_clase.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    docentes = Docente.query.order_by(Docente.apellido).all()
    aulas = Aula.query.order_by(Aula.nombre_aula).all()

    return render_template(
        'clases/list.html',
        clases=paginacion.items,
        paginacion=paginacion,
        docentes=docentes,
        aulas=aulas,
        ciclo_filtro=ciclo,
        docente_filtro=id_docente,
        aula_filtro=id_aula,
    )


# ==========================================
# DETALLE (incluye horarios de la clase)
# ==========================================
@clases_bp.route('/<int:id_clase>')
def detalle(id_clase):
    clase = Clase.query.get_or_404(id_clase)
    return render_template('clases/detalle.html', clase=clase, dias_semana=DIAS_SEMANA)


# ==========================================
# ALTA (Clase + primer Horario)
# ==========================================
@clases_bp.route('/nueva', methods=['GET', 'POST'])
def nueva():
    asignaturas = Asignatura.query.order_by(Asignatura.nombre_asignatura).all()
    docentes = Docente.query.order_by(Docente.apellido).all()
    aulas = Aula.query.order_by(Aula.nombre_aula).all()
    turnos = Turno.query.all()
    cursos = Curso.query.order_by(Curso.periodo_lectivo.desc(), Curso.anio, Curso.division).all()

    if request.method == 'POST':
        id_asignatura = request.form.get('id_asignatura', type=int)
        id_docente = request.form.get('id_docente', type=int)
        id_aula = request.form.get('id_aula', type=int)
        id_turno = request.form.get('id_turno', type=int)
        ciclo_lectivo = request.form.get('ciclo_lectivo', type=int)
        # Opcional: una Clase sin curso fijo es una electiva/optativa (usa clase_matricula)
        id_curso = request.form.get('id_curso', type=int) or None

        dia_semana = request.form.get('dia_semana')
        hora_desde = request.form.get('hora_desde')
        hora_hasta = request.form.get('hora_hasta')

        errores = []
        if not all([id_asignatura, id_docente, id_aula, id_turno, ciclo_lectivo]):
            errores.append('Todos los campos de la clase son obligatorios.')
        if not all([dia_semana, hora_desde, hora_hasta]):
            errores.append('Debe indicar día y horario de la clase.')
        elif hora_desde >= hora_hasta:
            errores.append('La hora de inicio debe ser menor a la hora de fin.')

        if id_curso:
            curso_seleccionado = Curso.query.get(id_curso)
            if not curso_seleccionado or curso_seleccionado.periodo_lectivo != ciclo_lectivo:
                errores.append('El curso seleccionado no corresponde al ciclo lectivo indicado.')

        if not errores:
            conflicto = verificar_solapamiento(id_aula, dia_semana, hora_desde, hora_hasta, ciclo_lectivo)
            if conflicto:
                clase_conflicto = conflicto.clase
                errores.append(
                    f'El aula ya está ocupada el {dia_semana} de {conflicto.hora_desde} a '
                    f'{conflicto.hora_hasta} por la clase de '
                    f'"{clase_conflicto.asignatura.nombre_asignatura}" (Docente: '
                    f'{clase_conflicto.docente.nombre} {clase_conflicto.docente.apellido}).'
                )

        if errores:
            for e in errores:
                flash(e, 'danger')
            return render_template(
                'clases/form.html',
                asignaturas=asignaturas, docentes=docentes, aulas=aulas, turnos=turnos,
                cursos=cursos, dias_semana=DIAS_SEMANA, clase=None, form=request.form,
            )

        nueva_clase = Clase(
            id_asignatura=id_asignatura,
            id_docente=id_docente,
            id_aula=id_aula,
            id_turno=id_turno,
            ciclo_lectivo=ciclo_lectivo,
            id_curso=id_curso,
        )
        db.session.add(nueva_clase)
        db.session.flush()  # obtenemos id_clase antes del commit final
        db.session.refresh(nueva_clase)  # Asegura que el objeto esté actualizado con la base de datos
        vincular_clase_a_matriculas_del_curso(nueva_clase)

        horario = Horario(
            id_clase=nueva_clase.id_clase,
            dia_semana=dia_semana,
            hora_desde=hora_desde,
            hora_hasta=hora_hasta,
        )
        db.session.add(horario)
        db.session.commit()

        flash('Clase creada correctamente.', 'success')
        return redirect(url_for('clases.detalle', id_clase=nueva_clase.id_clase))

    return render_template(
        'clases/form.html',
        asignaturas=asignaturas, docentes=docentes, aulas=aulas, turnos=turnos,
        cursos=cursos, dias_semana=DIAS_SEMANA, clase=None, form=None,
    )


# ==========================================
# EDICIÓN (datos generales de la clase)
# ==========================================
@clases_bp.route('/<int:id_clase>/editar', methods=['GET', 'POST'])
def editar(id_clase):
    clase = Clase.query.get_or_404(id_clase)
    asignaturas = Asignatura.query.order_by(Asignatura.nombre_asignatura).all()
    docentes = Docente.query.order_by(Docente.apellido).all()
    aulas = Aula.query.order_by(Aula.nombre_aula).all()
    turnos = Turno.query.all()
    cursos = Curso.query.order_by(Curso.periodo_lectivo.desc(), Curso.anio, Curso.division).all()

    if request.method == 'POST':
        id_asignatura = request.form.get('id_asignatura', type=int)
        id_docente = request.form.get('id_docente', type=int)
        id_aula = request.form.get('id_aula', type=int)
        id_turno = request.form.get('id_turno', type=int)
        ciclo_lectivo = request.form.get('ciclo_lectivo', type=int)
        id_curso = request.form.get('id_curso', type=int) or None

        errores = []
        if not all([id_asignatura, id_docente, id_aula, id_turno, ciclo_lectivo]):
            errores.append('Todos los campos son obligatorios.')

        if id_curso:
            curso_seleccionado = Curso.query.get(id_curso)
            if not curso_seleccionado or curso_seleccionado.periodo_lectivo != ciclo_lectivo:
                errores.append('El curso seleccionado no corresponde al ciclo lectivo indicado.')

        if not errores:
            # Revalidamos CADA horario existente contra la nueva combinación aula/ciclo
            for horario in clase.horarios:
                conflicto = verificar_solapamiento(
                    id_aula, horario.dia_semana, horario.hora_desde, horario.hora_hasta,
                    ciclo_lectivo, excluir_horario_id=horario.id_horario,
                )
                if conflicto:
                    clase_conflicto = conflicto.clase
                    errores.append(
                        f'El cambio genera un conflicto el {horario.dia_semana} '
                        f'({horario.hora_desde}-{horario.hora_hasta}) con la clase de '
                        f'"{clase_conflicto.asignatura.nombre_asignatura}".'
                    )
                    break

        if errores:
            for e in errores:
                flash(e, 'danger')
            return render_template(
                'clases/form.html',
                asignaturas=asignaturas, docentes=docentes, aulas=aulas, turnos=turnos,
                cursos=cursos, dias_semana=DIAS_SEMANA, clase=clase, form=request.form,
            )

        clase.id_asignatura = id_asignatura
        clase.id_docente = id_docente
        clase.id_aula = id_aula
        clase.id_turno = id_turno
        clase.ciclo_lectivo = ciclo_lectivo
        clase.id_curso = id_curso
        db.session.commit()

        flash('Clase actualizada correctamente.', 'success')
        return redirect(url_for('clases.detalle', id_clase=clase.id_clase))

    return render_template(
        'clases/form.html',
        asignaturas=asignaturas, docentes=docentes, aulas=aulas, turnos=turnos,
        cursos=cursos, dias_semana=DIAS_SEMANA, clase=clase, form=None,
    )


# ==========================================
# BAJA
# ==========================================
@clases_bp.route('/<int:id_clase>/eliminar', methods=['POST'])
def eliminar(id_clase):
    clase = Clase.query.get_or_404(id_clase)
    db.session.delete(clase)  # cascade="all, delete-orphan" borra también sus Horario
    db.session.commit()
    flash('Clase eliminada.', 'success')
    return redirect(url_for('clases.listar'))


# ==========================================
# HORARIOS DE UNA CLASE (alta / baja)
# ==========================================
@clases_bp.route('/<int:id_clase>/horarios/nuevo', methods=['POST'])
def agregar_horario(id_clase):
    clase = Clase.query.get_or_404(id_clase)

    dia_semana = request.form.get('dia_semana')
    hora_desde = request.form.get('hora_desde')
    hora_hasta = request.form.get('hora_hasta')

    if not all([dia_semana, hora_desde, hora_hasta]) or hora_desde >= hora_hasta:
        flash('Datos de horario inválidos: revise el día y el rango horario.', 'danger')
        return redirect(url_for('clases.detalle', id_clase=id_clase))

    conflicto = verificar_solapamiento(clase.id_aula, dia_semana, hora_desde, hora_hasta, clase.ciclo_lectivo)
    if conflicto:
        clase_conflicto = conflicto.clase
        flash(
            f'Conflicto de horario: el aula "{clase.aula.nombre_aula}" ya está ocupada el {dia_semana} '
            f'de {conflicto.hora_desde} a {conflicto.hora_hasta} por la clase de '
            f'"{clase_conflicto.asignatura.nombre_asignatura}".',
            'danger',
        )
        return redirect(url_for('clases.detalle', id_clase=id_clase))

    horario = Horario(id_clase=id_clase, dia_semana=dia_semana, hora_desde=hora_desde, hora_hasta=hora_hasta)
    db.session.add(horario)
    db.session.commit()
    flash('Horario agregado a la clase.', 'success')
    return redirect(url_for('clases.detalle', id_clase=id_clase))


@clases_bp.route('/horarios/<int:id_horario>/eliminar', methods=['POST'])
def eliminar_horario(id_horario):
    horario = Horario.query.get_or_404(id_horario)
    id_clase = horario.id_clase
    db.session.delete(horario)
    db.session.commit()
    flash('Horario eliminado.', 'success')
    return redirect(url_for('clases.detalle', id_clase=id_clase))