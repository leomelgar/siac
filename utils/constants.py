# -*- coding: utf-8 -*-
"""
Constantes del módulo de Calificaciones.

IMPORTANTE: los umbrales de aprobación y las instancias varían según lo
establecido por el ministerio de educacion de la provincia de Jujuy y el reglamento
institucional de cada colegio. Los valores acá definidos son un punto de
partida razonable y deben ajustarse al reglamento real del colegio.
"""

# Instancias trimestrales (coinciden con el valor guardado en Calificacion.instancia)
TRIMESTRE_1 = "1er Trimestre"
TRIMESTRE_2 = "2do Trimestre"
TRIMESTRE_3 = "3er Trimestre"

TRIMESTRES = [TRIMESTRE_1, TRIMESTRE_2, TRIMESTRE_3]

# Identificador corto <-> nombre de instancia, usado en las URLs (/trimestre/1)
TRIMESTRE_POR_NUMERO = {
    "1": TRIMESTRE_1,
    "2": TRIMESTRE_2,
    "3": TRIMESTRE_3,
}

# Instancias de mesas de examen (materias pendientes de aprobación)
MESA_DICIEMBRE = "Mesa Diciembre"
MESA_FEBRERO = "Mesa Febrero"

INSTANCIAS_MESA = [MESA_DICIEMBRE, MESA_FEBRERO]

# Nota mínima (numérica, escala 1-10) para considerar una instancia aprobada.
# Ajustar según reglamento (muchas jurisdicciones usan 6, otras 7).
NOTA_MINIMA_APROBACION = 6

# Conversión aproximada de calificaciones conceptuales a numéricas, usada
# únicamente para poder promediar. No se guarda en la base, es solo para cálculo.
ESCALA_CONCEPTUAL_A_NUMERICA = {
    "TEA": 8,   # Trayectoria Educativa Avanzada
    "TEP": 6,   # Trayectoria Educativa en Proceso
    "TED": 3,   # Trayectoria Educativa Discontinua
}

ESTADO_APROBADA = "Aprobada"
ESTADO_PENDIENTE_MESA = "Pendiente de mesa"
ESTADO_DESAPROBADA = "Desaprobada"
ESTADO_SIN_DATOS = "Sin notas cargadas"

# Estado inicial de un DetalleBoletin recién creado, antes de que se cierre
# ningún trimestre (coincide con el default del modelo DetalleBoletin.estado_materia).
ESTADO_CURSANDO = "Cursando"

# Mapeo entre el identificador de trimestre usado en las URLs y la columna
# de DetalleBoletin donde se "congela" esa nota al cerrar el trimestre.
TRIMESTRE_CAMPO_DETALLE = {
    "1": "nota_t1",
    "2": "nota_t2",
    "3": "nota_t3",
}
