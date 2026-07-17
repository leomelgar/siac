from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.colege import Alumno, Tutor, Persona, Colegio, alumno_tutor
from utils.db import db
from datetime import datetime as dt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

alumnos = Blueprint("alumnos", __name__)

@alumnos.route('/alumnos/home', methods=["POST","GET"]) #listado de alumnos
def home():
    alumnos = Alumno.query.all()
    cantidad = len(alumnos)
    # alumnos = Persona.query.filter(Persona.tipo_persona=='alumno')
    if request.method == "POST" and 'tag' in request.form:
        tag = request.form['tag']
        search = "%{}%".format(tag)
        alumnos = Alumno.query.filter(Alumno.apellido.like(search) | Alumno.legajo.like(search)).all()
        if not alumnos:
            flash('No existe registro...')
        else:
            return render_template('/alumnos/home.html', alumnos=alumnos, cantidad=cantidad)
    return render_template('/alumnos/home.html', alumnos=alumnos, cantidad=cantidad)

@alumnos.route('/inscripcion')
def inscripcion():
    return render_template('/alumnos/new.html')

# --- FUNCIÓN GENERADORA DE LEGAJO ---
def generar_nuevo_legajo():
    """Genera un legajo con el formato AAAA-NNNN (Ej: 2026-0001)"""
    año_actual = dt.now().year
    prefijo = f"{año_actual}-"
    
    # Buscamos el último legajo creado en este año
    ultimo_alumno = Alumno.query.filter(
        Alumno.legajo.like(f"{prefijo}%")
    ).order_by(Alumno.legajo.desc()).first()
    
    if ultimo_alumno:
        # Si existe "2026-0045", separamos por el guion y tomamos el "0045"
        ultimo_numero = int(ultimo_alumno.legajo.split('-')[1])
        nuevo_numero = ultimo_numero + 1
    else:
        # Es el primer alumno del año
        nuevo_numero = 1
        
    # Formateamos el número para que siempre tenga 4 dígitos (rellena con ceros a la izquierda)
    return f"{prefijo}{nuevo_numero:04d}"

@alumnos.route('/newAlumno', methods=['POST'])
def new_alumno():
    colegio = Colegio.query.first() 
    
    if request.method == 'POST':
        try:
            # 1. Capturar fechas primero
            f_t = request.form.get('fecha_nacimiento_t')
            f_a = request.form.get('fecha_nacimiento')
            
            # VALIDACIÓN: Verificar que las fechas no estén vacías o compuestas solo por espacios
            if not f_t or not f_t.strip():
                flash('La fecha de nacimiento del tutor es obligatoria.', 'danger')
                return redirect(url_for('alumnos.inscripcion'))
                
            if not f_a or not f_a.strip():
                flash('La fecha de nacimiento del alumno es obligatoria.', 'danger')
                return redirect(url_for('alumnos.inscripcion'))
            #asignar booleano al campo legal
            legal=request.form.get('legal')
            if legal=='True':
                l=True
            else:
                l=False
            # 2. Crear el Tutor
            nuevo_tutor = Tutor(
                nombre=request.form['nombre_t'],
                apellido=request.form['apellido_t'],
                dni=request.form['dni_t'],
                fecha_nacimiento=dt.strptime(f_t.strip(), '%Y-%m-%d').date(),
                direccion=request.form['direccion_t'],
                telefono=request.form.get('telefono_t'),
                email=request.form.get('email_t'),
                genero=request.form['genero_t'],
                parentesco=request.form.get('parentesco'),
                ocupacion=request.form.get('ocupacion'),
                legal=l
            )
            db.session.add(nuevo_tutor)
            
            # 3. Generar Legajo
            nuevo_legajo = generar_nuevo_legajo()
            
            # 4. Crear el Alumno
            nuevo_alumno = Alumno(
                nombre=request.form['nombre'],
                apellido=request.form['apellido'],
                dni=request.form['dni'],
                fecha_nacimiento=dt.strptime(f_a.strip(), '%Y-%m-%d').date(),
                direccion=request.form['direccion'],
                telefono=request.form.get('telefono'),
                email=request.form.get('email'),
                genero=request.form['genero'],
                cuil=request.form['cuil'],
                legajo=nuevo_legajo,
                id_colegio=colegio.id_colegio if colegio else None 
            )
            db.session.add(nuevo_alumno)
            
            db.session.flush()
            
            # 5. Agregar la relación en la tabla intermedia
            db.session.execute(
                alumno_tutor.insert().values(alumno_id=nuevo_alumno.id, tutor_id=nuevo_tutor.id)
            )
            
            # 6. Confirmar todos los cambios
            db.session.commit()
            
            flash('Tutor y Alumno creados exitosamente.', 'success')
            return redirect(url_for('alumnos.view', id=nuevo_alumno.id))
            
        except ValueError:
            # Captura específica por si el formato de fecha no es 'YYYY-MM-DD'
            db.session.rollback()
            flash('El formato de las fechas ingresadas no es válido.', 'danger')
            return redirect(url_for('alumnos.inscripcion'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar los datos: {str(e)}', 'danger')
            return redirect(url_for('alumnos.inscripcion'))

    return redirect(url_for('alumnos.home'))

#funcion para calcular la edad del alumno
def calculateAge(birthDate):#funcion para calcular la edad del alumno
    today = dt.today()
    age = today.year-birthDate.year-((today.month, today.day)<(birthDate.month, birthDate.day))
    return age

@alumnos.route('/alumnos/view/<id>', methods=["GET"]) #detalle de alumno
def view(id):
    #alumnos = Alumno.query.options(joinedload(Alumno.tutores)).all()#para traer todos los alumnos con sus tutores
    #alumno = Alumno.query.options(joinedload(Alumno.tutores)).get(id)
    alumno = db.session.query(Alumno).options(joinedload(Alumno.tutores)).get(id)
    #alumno = Alumno.query.get(id)
    #tutor = alumno_tutor.query.get(tutor_id==alumno.id)
    age = calculateAge(alumno.fecha_nacimiento)
    return render_template('/alumnos/detailAlumno.html', alumno=alumno, age=age)

@alumnos.route('/alumnos/update/<alumno>', methods=["POST","GET"])
def update_alumno(alumno):
    alumno = Alumno.query.get(alumno)
    if request.method == "POST":
        alumno.nombre = request.form['nombre']
        alumno.apellido = request.form['apellido']
        alumno.cuil = request.form['cuil']
        alumno.fecha_nacimiento = request.form['fecha_nacimiento']
        alumno.genero = request.form['genero']
        alumno.direccion = request.form['direccion']
        alumno.telefono = request.form['telefono']
        alumno.email = request.form['email']
        #----------actualizar datos tutor ----------
        # for i, tutor in enumerate(alumno.tutores):
        #     tutor.nombre = request.form[f'nombre_t']
        #     tutor.apellido = request.form[f'apellido_t']
        #     tutor.fecha_nacimiento = request.form[f'fecha_nacimiento_t']
        #     tutor.genero = request.form[f'genero_t']
        #     tutor.direccion = request.form[f'direccion_t']
        #     tutor.telefono = request.form[f'telefono_t']
        #     tutor.email = request.form[f'email_t']
        db.session.commit()
        flash('Datos Actualizados!')
        return redirect(url_for('alumnos.view', id=alumno.id))
    return render_template("/alumnos/updateAlumno.html", alumno=alumno)

@alumnos.route('/alumnos/update_tutor/<alumno>', methods=["POST","GET"])
def update_tutor(alumno):
    alumno = Alumno.query.get(alumno)
    if request.method == "POST":
        #----------actualizar datos tutor ----------
        for i, tutor in enumerate(alumno.tutores):
            tutor.nombre = request.form[f'nombre_t']
            tutor.apellido = request.form[f'apellido_t']
            tutor.fecha_nacimiento = request.form[f'fecha_nacimiento_t']
            tutor.genero = request.form[f'genero_t']
            tutor.direccion = request.form[f'direccion_t']
            tutor.telefono = request.form[f'telefono_t']
            tutor.email = request.form[f'email_t']
        db.session.commit()
        flash('Datos Actualizados!')
        return redirect(url_for('alumnos.view', id=alumno.id))
    return render_template("/alumnos/updateTutor.html", alumno=alumno)