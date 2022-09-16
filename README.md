## SIAC - Sistema Integral de Administracion de un Colegio

Este proyecto tiene como base un ejemplo CRUD realizado por FaztWeb con flask, mysql y SQLAlchemy en Python.
## Descripcion del Proyecto
Es un sistema para usar en un colegio secundario para gestionar los docentes y alumnos. 
## Gestion Docente
    -   CRUD de docentes 
    -   control de asistencia
## Gestion Alumnos
    -   CRUD de alumnos
        -   pre-inscripcion, se registran los datos del potencial alumno como asi tambien de un tutor responsable.
    -   Matricula. es la inscripcion del alumno.
    -   Control de asistencia

### Manual Installation

##### Requirements

* Python3
* Mysql

before run the app you must create the following environnment variables:

```
MYSQL_USER=
MYSQL_PASSWORD=
MYSQL_DATABASE=
MYSQL_HOST=
MYSQL_PORT=
```

```
git clone https://github.com/leomelgar/siac
cd siac
pip install -r requirements.txt
python index.py
```
