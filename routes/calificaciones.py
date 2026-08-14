# -*- coding: utf-8 -*-
"""
Blueprint de Calificaciones.

Basado en el modelo real del sistema (Persona con herencia por tabla
conjunta para Alumno/Docente/Tutor, Matricula, Boletin/DetalleBoletin,
etc). Notas sobre ese modelo relevantes para este blueprint:

  - `db` se importa desde `utils.db` (donde vive en el proyecto).
  - Alumno y Docente heredan de Persona: `id`, `nombre`, `apellido`, `dni`
    están en la tabla `persona`, no en `alumno`/`docente`. Calificacion.id_alumno
    y Clase.id_docente apuntan a `persona.id` vía la FK de la subclase, así
    que `alumno.id` / `docente.id` siguen siendo el identificador correcto.
  - Asignatura usa `nombre_asignatura` (no `nombre`). Turno usa `nombre_turno`.
  - Curso usa `anio` (string, ej "5to") + `division` (string, ej "A") +
    `periodo_lectivo` (int), y expone `nombre_completo()`.
  - Clase usa `ciclo_lectivo` (int) y Matricula usa `periodo_lectivo` (int):
    ambos deben coincidir para el mismo año escolar; se asume que la app
    los carga siempre con el mismo valor.
  - Matricula.alumno es la relación hacia Alumno (`back_populates='matriculas'`).
  - Es un sistema de un solo colegio: no se filtra por `id_colegio` en las
    consultas (si en el futuro hay más de un Colegio, agregar el filtro).
  - Boletin/DetalleBoletin son el documento OFICIAL, que se congela de forma
    explícita al cerrar cada trimestre y al cerrar las mesas (ver
    `cerrar_trimestre` y `cerrar_mesas` más abajo) — no se recalculan solos
    en cada carga de Calificacion.
  - No se implementa acá el control de permisos por Rol/Usuario (que un
    docente solo pueda cargar sus propias clases): se deja el gancho pero
    no se fuerza, porque depende de cómo esté armado el login en la app.

Registrar el blueprint en la app principal con, por ejemplo:

    from blueprints.calificaciones.routes import calificaciones_bp
    app.register_blueprint(calificaciones_bp)
"""
from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
)

from utils.db import db
from models.colege import (
    Clase,
    Calificacion,
    Alumno,
    Curso,
    Asignatura,
    Docente,
    Matricula,
)

from utils.constants import (
    TRIMESTRE_POR_NUMERO,
    TRIMESTRES,
    INSTANCIAS_MESA,
    MESA_DICIEMBRE,
    MESA_FEBRERO,
)
from utils.services import (
    obtener_alumnos_de_clase,
    notas_por_instancia,
    promedio_trimestral,
    resultado_final_materia,
    alumnos_con_materia_pendiente,
    cerrar_trimestre_clase,
    cerrar_mesas_clase,
)

calificaciones_bp = Blueprint(
    "calificaciones",
    __name__,
    url_prefix="/calificaciones",
    template_folder="templates",
)


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _ciclo_lectivo_actual():
    return datetime.utcnow().year


def _get_clase_o_404(id_clase):
    clase = Clase.query.get(id_clase)
    if clase is None:
        abort(404)
    return clase


def _upsert_calificacion(id_alumno, id_clase, instancia, valor, observaciones):
    """Crea o actualiza la calificación de un alumno para una instancia dada."""
    valor = (valor or "").strip()
    calificacion = Calificacion.query.filter_by(
        id_alumno=id_alumno, id_clase=id_clase, instancia=instancia
    ).first()

    if not valor:
        # Nota vacía: si ya existía una carga previa, se elimina; si no
        # existía, no se hace nada (permite dejar celdas en blanco).
        if calificacion is not None:
            db.session.delete(calificacion)
        return

    if calificacion is None:
        calificacion = Calificacion(
            id_alumno=id_alumno,
            id_clase=id_clase,
            instancia=instancia,
            valor=valor,
            observaciones=observaciones,
        )
        db.session.add(calificacion)
    else:
        calificacion.valor = valor
        calificacion.observaciones = observaciones
        calificacion.fecha_carga = datetime.utcnow()


# ---------------------------------------------------------------------------
# Panel principal
# ---------------------------------------------------------------------------

@calificaciones_bp.route("/")
def index():
    ciclo_lectivo = request.args.get("ciclo_lectivo", type=int) or _ciclo_lectivo_actual()
    return render_template(
        "calificaciones/index.html",
        ciclo_lectivo=ciclo_lectivo,
    )


# ---------------------------------------------------------------------------
# Listado de clases (para elegir dónde cargar notas)
# ---------------------------------------------------------------------------

@calificaciones_bp.route("/clases")
def listar_clases():
    ciclo_lectivo = request.args.get("ciclo_lectivo", type=int) or _ciclo_lectivo_actual()
    id_docente = request.args.get("id_docente", type=int)
    id_curso = request.args.get("id_curso", type=int)

    query = Clase.query.filter_by(ciclo_lectivo=ciclo_lectivo)
    if id_docente:
        query = query.filter_by(id_docente=id_docente)
    if id_curso:
        query = query.filter_by(id_curso=id_curso)

    clases = query.join(Asignatura).order_by(Asignatura.nombre_asignatura).all()

    return render_template(
        "calificaciones/listar_clases.html",
        clases=clases,
        ciclo_lectivo=ciclo_lectivo,
        cursos=Curso.query.filter_by(periodo_lectivo=ciclo_lectivo)
        .order_by(Curso.anio, Curso.division)
        .all(),
        docentes=Docente.query.order_by(Docente.apellido).all(),
        id_docente_filtro=id_docente,
        id_curso_filtro=id_curso,
    )


# ---------------------------------------------------------------------------
# Carga de notas trimestrales (planilla por clase)
# ---------------------------------------------------------------------------

@calificaciones_bp.route(
    "/clase/<int:id_clase>/trimestre/<string:num_trimestre>",
    methods=["GET", "POST"],
)
def planilla_trimestre(id_clase, num_trimestre):
    clase = _get_clase_o_404(id_clase)
    instancia = TRIMESTRE_POR_NUMERO.get(num_trimestre)
    if instancia is None:
        abort(404)

    alumnos = obtener_alumnos_de_clase(clase)

    if request.method == "POST":
        for alumno in alumnos:
            valor = request.form.get(f"nota_{alumno.id}", "")
            observaciones = request.form.get(f"obs_{alumno.id}", "").strip() or None
            _upsert_calificacion(alumno.id, clase.id_clase, instancia, valor, observaciones)
        db.session.commit()
        flash(f"Notas de {instancia} guardadas correctamente.", "success")
        return redirect(
            url_for(
                "calificaciones.planilla_trimestre",
                id_clase=id_clase,
                num_trimestre=num_trimestre,
            )
        )

    calificaciones_existentes = Calificacion.query.filter_by(
        id_clase=id_clase, instancia=instancia
    ).all()
    notas_por_alumno = {c.id_alumno: c for c in calificaciones_existentes}

    return render_template(
        "calificaciones/planilla_trimestre.html",
        clase=clase,
        instancia=instancia,
        num_trimestre=num_trimestre,
        alumnos=alumnos,
        notas_por_alumno=notas_por_alumno,
        trimestres=TRIMESTRES,
    )


# ---------------------------------------------------------------------------
# Boletín / resumen de una clase (vista del docente: todos los alumnos)
# ---------------------------------------------------------------------------

@calificaciones_bp.route("/clase/<int:id_clase>/resumen")
def resumen_clase(id_clase):
    clase = _get_clase_o_404(id_clase)
    alumnos = obtener_alumnos_de_clase(clase)
    calificaciones = Calificacion.query.filter_by(id_clase=id_clase).all()

    por_alumno = {}
    for alumno in alumnos:
        cals_alumno = [c for c in calificaciones if c.id_alumno == alumno.id]
        por_alumno[alumno.id] = {
            "notas": notas_por_instancia(cals_alumno),
            "resultado": resultado_final_materia(cals_alumno),
        }

    return render_template(
        "calificaciones/resumen_clase.html",
        clase=clase,
        alumnos=alumnos,
        por_alumno=por_alumno,
        trimestres=TRIMESTRES,
    )


# ---------------------------------------------------------------------------
# Cierre de trimestre: congela las notas vigentes en el boletín OFICIAL
# (DetalleBoletin). Se hace por clase, para todos sus alumnos a la vez.
# Pensado para que lo dispare preceptoría (o un directivo) al terminar el
# trimestre, no automáticamente en cada carga del docente.
# ---------------------------------------------------------------------------

@calificaciones_bp.route(
    "/clase/<int:id_clase>/cerrar-trimestre/<string:num_trimestre>", methods=["POST"]
)
def cerrar_trimestre(id_clase, num_trimestre):
    clase = _get_clase_o_404(id_clase)
    if num_trimestre not in TRIMESTRE_POR_NUMERO:
        abort(404)

    cerrar_trimestre_clase(clase, num_trimestre)
    db.session.commit()
    flash(
        f"{TRIMESTRE_POR_NUMERO[num_trimestre]} cerrado: las notas quedaron "
        f"congeladas en el boletín oficial.",
        "success",
    )
    return redirect(url_for("calificaciones.resumen_clase", id_clase=id_clase))


# ---------------------------------------------------------------------------
# Boletín de un alumno (todas sus materias del ciclo lectivo)
# ---------------------------------------------------------------------------

@calificaciones_bp.route("/alumno/<int:id_alumno>/boletin")
def boletin_alumno(id_alumno):
    alumno = Alumno.query.get_or_404(id_alumno)
    ciclo_lectivo = request.args.get("ciclo_lectivo", type=int) or _ciclo_lectivo_actual()

    # Clases en las que el alumno está matriculado durante el ciclo lectivo.
    clases = (
        Clase.query.filter_by(ciclo_lectivo=ciclo_lectivo)
        .join(Clase.matriculas)
        .filter_by(id_alumno=id_alumno)
        .all()
    )

    materias = []
    for clase in clases:
        cals = Calificacion.query.filter_by(id_alumno=id_alumno, id_clase=clase.id_clase).all()
        materias.append(
            {
                "clase": clase,
                "notas": notas_por_instancia(cals),
                "resultado": resultado_final_materia(cals),
            }
        )

    return render_template(
        "calificaciones/boletin_alumno.html",
        alumno=alumno,
        materias=materias,
        ciclo_lectivo=ciclo_lectivo,
        trimestres=TRIMESTRES,
    )


# ---------------------------------------------------------------------------
# Mesas de examen (diciembre / febrero)
# ---------------------------------------------------------------------------

@calificaciones_bp.route("/mesas")
def mesas():
    ciclo_lectivo = request.args.get("ciclo_lectivo", type=int) or _ciclo_lectivo_actual()
    clases = Clase.query.filter_by(ciclo_lectivo=ciclo_lectivo).join(Asignatura).order_by(
        Asignatura.nombre_asignatura
    ).all()

    resumen_por_clase = []
    for clase in clases:
        calificaciones = Calificacion.query.filter_by(id_clase=clase.id_clase).all()
        pendientes = alumnos_con_materia_pendiente(clase, calificaciones)
        if pendientes:
            resumen_por_clase.append({"clase": clase, "pendientes": pendientes})

    return render_template(
        "calificaciones/mesas_listado.html",
        ciclo_lectivo=ciclo_lectivo,
        resumen_por_clase=resumen_por_clase,
    )


@calificaciones_bp.route(
    "/clase/<int:id_clase>/mesa/<string:instancia>", methods=["GET", "POST"]
)
def planilla_mesa(id_clase, instancia):
    if instancia not in INSTANCIAS_MESA:
        abort(404)

    clase = _get_clase_o_404(id_clase)
    calificaciones_clase = Calificacion.query.filter_by(id_clase=id_clase).all()
    pendientes = alumnos_con_materia_pendiente(clase, calificaciones_clase)
    alumnos = [alumno for alumno, _resultado in pendientes]

    if request.method == "POST":
        for alumno in alumnos:
            valor = request.form.get(f"nota_{alumno.id}", "")
            observaciones = request.form.get(f"obs_{alumno.id}", "").strip() or None
            _upsert_calificacion(alumno.id, clase.id_clase, instancia, valor, observaciones)
        db.session.commit()
        flash(f"Notas de {instancia} guardadas correctamente.", "success")
        return redirect(
            url_for("calificaciones.planilla_mesa", id_clase=id_clase, instancia=instancia)
        )

    calificaciones_instancia = Calificacion.query.filter_by(
        id_clase=id_clase, instancia=instancia
    ).all()
    notas_por_alumno = {c.id_alumno: c for c in calificaciones_instancia}

    return render_template(
        "calificaciones/planilla_mesa.html",
        clase=clase,
        instancia=instancia,
        alumnos=alumnos,
        notas_por_alumno=notas_por_alumno,
    )


@calificaciones_bp.route("/clase/<int:id_clase>/cerrar-mesas", methods=["POST"])
def cerrar_mesas(id_clase):
    """Congela en DetalleBoletin el resultado final (mesas + estado_materia)."""
    clase = _get_clase_o_404(id_clase)
    cerrar_mesas_clase(clase)
    db.session.commit()
    flash("Resultado de mesas congelado en el boletín oficial.", "success")
    return redirect(url_for("calificaciones.mesas", ciclo_lectivo=clase.ciclo_lectivo))


# ---------------------------------------------------------------------------
# Boletín OFICIAL de un alumno (lee Boletin/DetalleBoletin, ya congelados,
# a diferencia de /alumno/<id>/boletin que muestra el avance en vivo desde
# Calificacion). Sirve para imprimir o para consultar el documento cerrado.
# ---------------------------------------------------------------------------

@calificaciones_bp.route("/alumno/<int:id_alumno>/boletin-oficial")
def boletin_oficial(id_alumno):
    alumno = Alumno.query.get_or_404(id_alumno)
    periodo_lectivo = request.args.get("periodo_lectivo", type=int) or _ciclo_lectivo_actual()

    matricula = Matricula.query.filter_by(
        id_alumno=id_alumno, periodo_lectivo=periodo_lectivo
    ).first()
    boletin = matricula.boletin if matricula else None
    detalles = boletin.detalles if boletin else []

    return render_template(
        "calificaciones/boletin_oficial.html",
        alumno=alumno,
        periodo_lectivo=periodo_lectivo,
        boletin=boletin,
        detalles=detalles,
    )


# ---------------------------------------------------------------------------
# Eliminar una carga puntual (corrección de error de tipeo/instancia)
# ---------------------------------------------------------------------------

@calificaciones_bp.route("/calificacion/<int:id_calificacion>/eliminar", methods=["POST"])
def eliminar_calificacion(id_calificacion):
    calificacion = Calificacion.query.get_or_404(id_calificacion)
    id_clase = calificacion.id_clase
    instancia = calificacion.instancia
    db.session.delete(calificacion)
    db.session.commit()
    flash("Calificación eliminada.", "info")

    if instancia in INSTANCIAS_MESA:
        return redirect(
            url_for("calificaciones.planilla_mesa", id_clase=id_clase, instancia=instancia)
        )
    num_trimestre = next(
        (num for num, nombre in TRIMESTRE_POR_NUMERO.items() if nombre == instancia), "1"
    )
    return redirect(
        url_for("calificaciones.planilla_trimestre", id_clase=id_clase, num_trimestre=num_trimestre)
    )
