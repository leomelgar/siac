## SIAC - Sistema Integral de Administracion de un Colegio

Este proyecto tiene como base un ejemplo CRUD realizado con flask, Mariadb y SQLAlchemy en Python.
## Descripcion del Proyecto
Es un sistema para usar en un colegio secundario, gestiona las inscripciones de alumnos, docentes, clases, asistencias y calificaciones de un periodo lectivo. 
## Gestion Docente
    -   CRUD de docentes 
## Gestion Alumnos
    -   CRUD de alumnos
        -   pre-inscripcion, se registran los datos del potencial alumno como asi tambien de un padre o tutor legal.

### Manual Installation

##### Requirements
* Python3
* Mysql - Mariadb(actualmente, usando el driver pymysql)
* Flask, Flask-sqlAlquemy
### Configurar los parametros para la conexion con la base de datos, trabajar con variables de entorno del SO

###
git clone https://github.com/leomelgar/siac
cd siac
pip install -r requirements.txt
python index.py
```
