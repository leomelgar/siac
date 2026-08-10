from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, date

from utils.db import db
from models.colege import Clase, Alumno, Asistencia, Matricula, EstadoRegularidad, Horario

asistencia_bp = Blueprint('asistencia', __name__, url_prefix='/asistencia')

DIAS_SEMANA = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

VALORES_FALTA = {
    'Presente': 0.0,
    'Ausente': 1.0,
    'Llegada Tarde': 0.5,
    'Retiro Anticipado': 0.5,
}


# ------------------------------------------
# PANEL DIARIO (preceptor): qué clases se dictan hoy
# ------------------------------------------
@asistencia_bp.route('/panel', methods=['GET'])
@login_required
def panel_diario():
    fecha_str = request.args.get('fecha')
    fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date() if fecha_str else date.today()
    dia_nombre = DIAS_SEMANA[fecha.weekday()]

    clases_del_dia = (
        Clase.query
        .join(Horario, Horario.id_clase == Clase.id_clase)
        .filter(Horario.dia_semana == dia_nombre, Clase.ciclo_lectivo == fecha.year)
        .all()
    )

    return render_template(
        'asistencia/panel.html',
        clases=clases_del_dia,
        fecha=fecha,
        dia_nombre=dia_nombre
    )


# ------------------------------------------
# TOMAR ASISTENCIA de una clase en una fecha
# ------------------------------------------
@asistencia_bp.route('/clase/<int:id_clase>', methods=['GET'])
@login_required
def tomar_asistencia(id_clase):
    clase = Clase.query.get_or_404(id_clase)

    fecha_str = request.args.get('fecha')
    fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date() if fecha_str else date.today()

    if clase.id_curso:
        # Camino principal: la clase pertenece a un Curso -> alumnos matriculados en ese curso
        alumnos = (
            Alumno.query
            .join(Matricula, Matricula.id_alumno == Alumno.id)
            .filter(Matricula.id_curso == clase.id_curso)
            .order_by(Alumno.apellido, Alumno.nombre)
            .all()
        )
    else:
        # Excepción: clase sin curso fijo (electiva/optativa) -> inscripción puntual vía clase_matricula
        alumnos = (
            Alumno.query
            .join(Matricula, Matricula.id_alumno == Alumno.id)
            .join(Matricula.clases_inscriptas)
            .filter(Clase.id_clase == id_clase)
            .order_by(Alumno.apellido, Alumno.nombre)
            .all()
        )

    registros_existentes = {
        a.id_alumno: a
        for a in Asistencia.query.filter_by(id_clase=id_clase, fecha=fecha).all()
    }

    return render_template(
        'asistencia/tomar.html',
        clase=clase,
        alumnos=alumnos,
        fecha=fecha,
        registros=registros_existentes,
        tipos=list(VALORES_FALTA.keys())
    )


@asistencia_bp.route('/clase/<int:id_clase>', methods=['POST'])
@login_required
def guardar_asistencia(id_clase):
    clase = Clase.query.get_or_404(id_clase)
    fecha_str = request.form.get('fecha')
    fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()

    alumnos_ids = request.form.getlist('id_alumno')

    for id_alumno_str in alumnos_ids:
        id_alumno = int(id_alumno_str)
        tipo_registro = request.form.get(f'tipo_{id_alumno}', 'Presente')
        valor_falta = VALORES_FALTA.get(tipo_registro, 0.0)

        registro = Asistencia.query.filter_by(
            id_alumno=id_alumno, id_clase=id_clase, fecha=fecha
        ).first()

        if registro:
            registro.tipo_registro = tipo_registro
            registro.valor_falta = valor_falta
        else:
            registro = Asistencia(
                id_alumno=id_alumno,
                id_clase=id_clase,
                fecha=fecha,
                tipo_registro=tipo_registro,
                valor_falta=valor_falta
            )
            db.session.add(registro)

        _actualizar_regularidad(id_alumno, clase.ciclo_lectivo)

    db.session.commit()
    flash('Asistencia guardada correctamente.', 'success')
    return redirect(url_for('curso.listar'))


# ------------------------------------------
# HISTORIAL DE UN ALUMNO
# ------------------------------------------
@asistencia_bp.route('/alumno/<int:id_alumno>', methods=['GET'])
@login_required
def historial_alumno(id_alumno):
    alumno = Alumno.query.get_or_404(id_alumno)
    periodo = request.args.get('periodo', type=int, default=datetime.now().year)

    asistencias = (
        Asistencia.query
        .join(Clase, Clase.id_clase == Asistencia.id_clase)
        .filter(Asistencia.id_alumno == id_alumno, Clase.ciclo_lectivo == periodo)
        .order_by(Asistencia.fecha.desc())
        .all()
    )

    matricula = Matricula.query.filter_by(id_alumno=id_alumno, periodo_lectivo=periodo).first()
    estado = matricula.estado_regularidad if matricula else None

    return render_template(
        'asistencia/historial.html',
        alumno=alumno,
        asistencias=asistencias,
        estado=estado,
        periodo=periodo
    )


# ------------------------------------------
# JUSTIFICAR UNA FALTA
# ------------------------------------------
@asistencia_bp.route('/justificar/<int:id_asistencia>', methods=['GET', 'POST'])
@login_required
def justificar(id_asistencia):
    registro = Asistencia.query.get_or_404(id_asistencia)

    if request.method == 'POST':
        registro.justificada = True
        registro.motivo_justificacion = request.form.get('motivo')
        registro.fecha_justificacion = date.today()
        db.session.commit()

        _actualizar_regularidad(registro.id_alumno, registro.clase.ciclo_lectivo)
        db.session.commit()

        flash('Falta justificada correctamente.', 'success')
        return redirect(url_for('asistencia.historial_alumno', id_alumno=registro.id_alumno))

    return render_template('asistencia/justificar.html', registro=registro)


# ------------------------------------------
# ESTADO DE REGULARIDAD DE UNA MATRÍCULA
# ------------------------------------------
@asistencia_bp.route('/regularidad/<int:id_matricula>', methods=['GET'])
@login_required
def ver_regularidad(id_matricula):
    matricula = Matricula.query.get_or_404(id_matricula)
    estado = matricula.estado_regularidad
    tramites = matricula.reincorporaciones

    return render_template(
        'asistencia/regularidad.html',
        matricula=matricula,
        estado=estado,
        tramites=tramites
    )


# ------------------------------------------
# HELPER: recalcula totales de EstadoRegularidad
# ------------------------------------------
def _actualizar_regularidad(id_alumno, ciclo_lectivo):
    matricula = Matricula.query.filter_by(
        id_alumno=id_alumno, periodo_lectivo=ciclo_lectivo
    ).first()
    if not matricula:
        return

    total = db.session.query(db.func.sum(Asistencia.valor_falta)).join(
        Clase, Asistencia.id_clase == Clase.id_clase
    ).filter(
        Asistencia.id_alumno == id_alumno,
        Clase.ciclo_lectivo == ciclo_lectivo,
        Asistencia.justificada == False
    ).scalar() or 0.0

    total_justificadas = db.session.query(db.func.sum(Asistencia.valor_falta)).join(
        Clase, Asistencia.id_clase == Clase.id_clase
    ).filter(
        Asistencia.id_alumno == id_alumno,
        Clase.ciclo_lectivo == ciclo_lectivo,
        Asistencia.justificada == True
    ).scalar() or 0.0

    estado = matricula.estado_regularidad
    if not estado:
        estado = EstadoRegularidad(id_matricula=matricula.id_matricula)
        db.session.add(estado)

    estado.total_faltas = total
    estado.total_faltas_justificadas = total_justificadas
    estado.verificar_estado()