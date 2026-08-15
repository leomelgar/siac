""" Sincronización Matricula <-> Clase (tabla intermedia clase_matricula).

Estas dos funciones son las que faltan en el flujo de alta de Matricula y
de alta de Clase. Sin ellas, `clase.matriculas` queda siempre vacío aunque
el alumno esté correctamente matriculado en el curso.

UBICACIÓN SUGERIDA: este archivo puede vivir en utils/matriculacion.py (o
donde tengan el resto de la lógica de negocio que no es específica de un
blueprint), porque lo van a necesitar tanto desde el alta de alumnos/
matrículas como desde el alta de clases. """

from models.colege import Clase, Matricula


def vincular_matricula_a_clases_del_curso(matricula):
    """
    Llamar justo después de crear (y hacer flush/commit de) una Matricula.
    Inscribe al alumno en todas las Clases ya existentes para el mismo
    curso y el mismo ciclo lectivo.
    """
    if not matricula.id_curso:
        return
    clases = Clase.query.filter_by(
        id_curso=matricula.id_curso, ciclo_lectivo=matricula.periodo_lectivo
    ).all()
    for clase in clases:
        if matricula not in clase.matriculas:
            clase.matriculas.append(matricula)


def vincular_clase_a_matriculas_del_curso(clase):
    """
    Llamar justo después de crear (y hacer flush/commit de) una Clase.
    Inscribe en ella a todos los alumnos ya matriculados en ese curso
    para el mismo ciclo lectivo.
    """
    if not clase.id_curso:
        return
    matriculas = Matricula.query.filter_by(
        id_curso=clase.id_curso, periodo_lectivo=clase.ciclo_lectivo
    ).all()
    for matricula in matriculas:
        if matricula not in clase.matriculas:
            clase.matriculas.append(matricula)