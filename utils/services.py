# -*- coding: utf-8 -*-
"""
Lógica de cálculo de promedios y estados de materia.

Se separa de las rutas (routes.py) para poder testear estas funciones
de forma aislada y para reutilizarlas tanto en la vista de boletín del
docente como en la del alumno y en el armado de mesas.
"""
from statistics import mean

from utils.db import db
from models.colege import (
    Calificacion,
    Matricula,
    Boletin,
    DetalleBoletin,
)

from .constants import (
    TRIMESTRES,
    TRIMESTRE_POR_NUMERO,
    TRIMESTRE_CAMPO_DETALLE,
    MESA_DICIEMBRE,
    MESA_FEBRERO,
    NOTA_MINIMA_APROBACION,
    ESCALA_CONCEPTUAL_A_NUMERICA,
    ESTADO_APROBADA,
    ESTADO_PENDIENTE_MESA,
    ESTADO_DESAPROBADA,
    ESTADO_SIN_DATOS,
)


def valor_a_numero(valor):
    """
    Convierte el campo Calificacion.valor (string) a un número para poder
    promediar. Soporta notas numéricas ("8", "7.5") y conceptuales
    (TEA/TEP/TED). Devuelve None si no se puede interpretar.
    """
    if valor is None:
        return None
    valor = valor.strip().upper()
    if not valor:
        return None
    if valor in ESCALA_CONCEPTUAL_A_NUMERICA:
        return ESCALA_CONCEPTUAL_A_NUMERICA[valor]
    try:
        return float(valor.replace(",", "."))
    except ValueError:
        return None


def obtener_alumnos_de_clase(clase):
    """
    Devuelve la lista de Alumno matriculados en una Clase, ordenados por
    apellido y nombre. Asume que Matricula tiene una relación `.alumno`
    hacia el modelo Alumno (ajustar el nombre del atributo si difiere).
    """
    alumnos = []
    for matricula in clase.matriculas:
        alumno = matricula.alumno
        if alumno is not None:
            alumnos.append(alumno)
    alumnos.sort(key=lambda a: (a.apellido or "", a.nombre or ""))
    return alumnos


def notas_por_instancia(calificaciones):
    """Indexa una lista de Calificacion por su campo `instancia`."""
    return {c.instancia: c for c in calificaciones}


def promedio_trimestral(calificaciones_alumno_clase):
    """
    Calcula el promedio de los 3 trimestres a partir de las calificaciones
    de un alumno en una clase. Solo tiene en cuenta trimestres con nota
    numérica válida; si falta alguno, igual promedia los presentes.
    Devuelve None si no hay ningún trimestre cargado.
    """
    por_instancia = notas_por_instancia(calificaciones_alumno_clase)
    valores = []
    for trimestre in TRIMESTRES:
        cal = por_instancia.get(trimestre)
        if cal is None:
            continue
        numero = valor_a_numero(cal.valor)
        if numero is not None:
            valores.append(numero)
    if not valores:
        return None
    return round(mean(valores), 2)


def resultado_final_materia(calificaciones_alumno_clase):
    """
    Determina el resultado final de una materia para un alumno, combinando
    el promedio trimestral con las mesas de diciembre/febrero si existieron.

    Regla aplicada (ajustable a reglamento institucional):
      1. Si el promedio de los 3 trimestres >= NOTA_MINIMA_APROBACION -> Aprobada.
      2. Si no, y rindió Mesa Diciembre con nota >= mínima -> Aprobada por mesa dic.
      3. Si no, y rindió Mesa Febrero con nota >= mínima -> Aprobada por mesa feb.
      4. Si rindió alguna mesa pero no alcanzó la nota -> Desaprobada.
      5. Si no rindió ninguna mesa y el promedio trimestral es insuficiente
         -> Pendiente de mesa.
      6. Si no hay ninguna nota cargada -> Sin notas cargadas.

    Devuelve un dict con: promedio_trimestral, nota_final, instancia_definitoria, estado.
    """
    por_instancia = notas_por_instancia(calificaciones_alumno_clase)
    promedio = promedio_trimestral(calificaciones_alumno_clase)

    if promedio is not None and promedio >= NOTA_MINIMA_APROBACION:
        return {
            "promedio_trimestral": promedio,
            "nota_final": promedio,
            "instancia_definitoria": "Trimestres",
            "estado": ESTADO_APROBADA,
        }

    for instancia in (MESA_DICIEMBRE, MESA_FEBRERO):
        cal_mesa = por_instancia.get(instancia)
        if cal_mesa is None:
            continue
        numero = valor_a_numero(cal_mesa.valor)
        if numero is not None and numero >= NOTA_MINIMA_APROBACION:
            return {
                "promedio_trimestral": promedio,
                "nota_final": numero,
                "instancia_definitoria": instancia,
                "estado": ESTADO_APROBADA,
            }
        elif numero is not None:
            # Rindió la mesa pero no alcanzó; si ya rindió febrero, queda desaprobada.
            if instancia == MESA_FEBRERO:
                return {
                    "promedio_trimestral": promedio,
                    "nota_final": numero,
                    "instancia_definitoria": instancia,
                    "estado": ESTADO_DESAPROBADA,
                }

    if promedio is None:
        return {
            "promedio_trimestral": None,
            "nota_final": None,
            "instancia_definitoria": None,
            "estado": ESTADO_SIN_DATOS,
        }

    return {
        "promedio_trimestral": promedio,
        "nota_final": None,
        "instancia_definitoria": None,
        "estado": ESTADO_PENDIENTE_MESA,
    }


def alumnos_con_materia_pendiente(clase, calificaciones_de_la_clase):
    """
    Dada una Clase y todas sus Calificaciones (de todos los alumnos),
    devuelve la lista de alumnos cuyo resultado final de la materia
    todavía no está aprobado (pendientes de rendir mesa).
    """
    from collections import defaultdict

    por_alumno = defaultdict(list)
    for cal in calificaciones_de_la_clase:
        por_alumno[cal.id_alumno].append(cal)

    pendientes = []
    for alumno in obtener_alumnos_de_clase(clase):
        resultado = resultado_final_materia(por_alumno.get(alumno.id, []))
        if resultado["estado"] in (ESTADO_PENDIENTE_MESA, ESTADO_DESAPROBADA):
            pendientes.append((alumno, resultado))
    return pendientes


# ---------------------------------------------------------------------------
# Boletín oficial (Boletin / DetalleBoletin)
#
# Calificacion es el registro "de trabajo" que cargan los docentes durante
# el año. Boletin/DetalleBoletin es el documento oficial que se congela al
# cerrar cada trimestre (y las mesas), tal como está pensado en el modelo:
# no se recalcula solo, requiere una acción explícita (botón "Cerrar
# trimestre" / "Cerrar mesas") disparada por preceptoría o por el sistema.
# ---------------------------------------------------------------------------

def obtener_matricula(id_alumno, periodo_lectivo):
    """Matrícula activa del alumno para un período lectivo dado."""
    return Matricula.query.filter_by(
        id_alumno=id_alumno, periodo_lectivo=periodo_lectivo
    ).first()


def obtener_o_crear_boletin(matricula):
    """Devuelve el Boletin (cabecera) de la matrícula, creándolo si no existe."""
    if matricula.boletin:
        return matricula.boletin
    boletin = Boletin(id_matricula=matricula.id_matricula)
    db.session.add(boletin)
    db.session.flush()
    return boletin


def obtener_o_crear_detalle(boletin, id_asignatura):
    """Devuelve la fila de DetalleBoletin de una asignatura, creándola si no existe."""
    detalle = next(
        (d for d in boletin.detalles if d.id_asignatura == id_asignatura), None
    )
    if detalle is None:
        detalle = DetalleBoletin(id_boletin=boletin.id_boletin, id_asignatura=id_asignatura)
        db.session.add(detalle)
        db.session.flush()
    return detalle


def cerrar_trimestre_clase(clase, num_trimestre):
    """
    Congela en DetalleBoletin (nota_t1/nota_t2/nota_t3) la nota del
    trimestre indicado, para todos los alumnos matriculados en la clase.
    No hace commit: quien llama a esta función es responsable de
    confirmarlo (permite envolver en una transacción más amplia).
    Devuelve la lista de DetalleBoletin tocados.
    """
    instancia = TRIMESTRE_POR_NUMERO[num_trimestre]
    campo = TRIMESTRE_CAMPO_DETALLE[num_trimestre]

    detalles_actualizados = []
    for alumno in obtener_alumnos_de_clase(clase):
        matricula = obtener_matricula(alumno.id, clase.ciclo_lectivo)
        if matricula is None:
            # Alumno sin matrícula vigente para ese ciclo lectivo: se omite
            # (situación anómala que conviene loguear/alertar en producción).
            continue
        boletin = obtener_o_crear_boletin(matricula)
        detalle = obtener_o_crear_detalle(boletin, clase.id_asignatura)
        calificacion = Calificacion.query.filter_by(
            id_alumno=alumno.id, id_clase=clase.id_clase, instancia=instancia
        ).first()
        setattr(detalle, campo, calificacion.valor if calificacion else None)
        detalles_actualizados.append(detalle)
    return detalles_actualizados


def cerrar_mesas_clase(clase):
    """
    Congela en DetalleBoletin las notas de Mesa Diciembre / Mesa Febrero y
    el estado_materia / promedio_anual finales, para los alumnos de la clase.
    No hace commit. Devuelve la lista de DetalleBoletin tocados.
    """
    calificaciones_clase = Calificacion.query.filter_by(id_clase=clase.id_clase).all()
    por_alumno = {}
    for cal in calificaciones_clase:
        por_alumno.setdefault(cal.id_alumno, []).append(cal)

    detalles_actualizados = []
    for alumno in obtener_alumnos_de_clase(clase):
        matricula = obtener_matricula(alumno.id, clase.ciclo_lectivo)
        if matricula is None:
            continue
        boletin = obtener_o_crear_boletin(matricula)
        detalle = obtener_o_crear_detalle(boletin, clase.id_asignatura)

        cals_alumno = por_alumno.get(alumno.id, [])
        notas = notas_por_instancia(cals_alumno)
        mesa_dic = notas.get(MESA_DICIEMBRE)
        mesa_feb = notas.get(MESA_FEBRERO)
        detalle.nota_diciembre = mesa_dic.valor if mesa_dic else None
        detalle.nota_marzo = mesa_feb.valor if mesa_feb else None

        resultado = resultado_final_materia(cals_alumno)
        detalle.estado_materia = resultado["estado"]
        if resultado["nota_final"] is not None:
            detalle.promedio_anual = resultado["nota_final"]

        detalles_actualizados.append(detalle)
    return detalles_actualizados
