from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.colege import Alumno, Tutor, Persona, Colegio, alumno_tutor
from utils.db import db
from datetime import datetime
from sqlalchemy.exc import IntegrityError

alumnos = Blueprint("alumnos", __name__)

@alumnos.route('/alumnos/home', methods=["POST","GET"]) #listado de alumnos
def home():
    alumnos = Alumno.query.all()
    if request.method == "POST" and 'tag' in request.form:
        tag = request.form['tag']
        search = "%{}%".format(tag)
        alumnos = Alumno.query.filter(Alumno.apellido.like(search))
        if not alumnos:
            flash('No existe registro...')
        else:
            return render_template('/alumnos/home.html', alumnos=alumnos)
    return render_template('/alumnos/home.html', alumnos=alumnos)

@alumnos.route('/inscripcion')
def inscripcion():
    return render_template('/alumnos/new.html')

""" @alumnos.route('/newTutor', methods=['POST'])
def new_tutor():
    # if request.method == 'POST':
    #     nombre = request.form['nombre']
    #     apellido = request.form['apellido']
    #     dni = request.form['dni']
    #     telefono  = request.form['telefono']
    #     email = request.form['email']
    #     direccion = request.form['direccion']
    #     parentesco = request.form['parentesco']
    #     legal = request.form['legal']
    
    #     new_tutor = Tutor(nombre, apellido, dni, telefono, email, direccion, parentesco, legal)
    #     db.session.add(new_tutor)
    #     db.session.commit()
    #     flash('Tutor añadido correctamente!')
    #     #return render_template('/alumnos/new.html')
    #     return redirect(url_for('alumnos.home'))
    if request.method == 'POST':
        try:
            # Capturar datos del formulario HTML
            fecha_nac = datetime.strptime(request.form['fecha_nacimiento'], '%Y-%m-%d').date()
            
            # Los checkboxes en HTML envían "on" si están marcados, o nada si no lo están
            es_legal = request.form.get('legal') == 'on'
            
            nuevo_tutor = Tutor(
                nombre=request.form['nombre'],
                apellido=request.form['apellido'],
                dni=request.form['dni'],
                fecha_nacimiento=fecha_nac,
                direccion=request.form['direccion'],
                telefono=request.form.get('telefono'),
                email=request.form.get('email'),
                genero=request.form['genero'],
                parentesco=request.form.get('parentesco'),
                ocupacion=request.form.get('ocupacion'),
                legal=es_legal
            )
            
            db.session.add(nuevo_tutor)
            db.session.commit()
            
            flash('Tutor creado exitosamente.', 'success')
            return redirect(url_for('inscripcion'))  # Redirige a la página de inscripción después de crear el tutor

        except IntegrityError:
            db.session.rollback()
            flash('Error: El DNI o Email ya se encuentra registrado.', 'danger')
        except Exception as e:
            flash(f'Error al crear el tutor: {str(e)}', 'danger')

    # Si es GET (acaba de entrar a la URL), mostramos el formulario vacío
    return render_template('alumnos.home.html') """
# --- FUNCIÓN GENERADORA DE LEGAJO ---
def generar_nuevo_legajo():
    """Genera un legajo con el formato AAAA-NNNN (Ej: 2026-0001)"""
    año_actual = datetime.datetime.now().year
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

""" @alumnos.route('/newAlumno', methods=['POST'])
def new_alumno():
    # if request.method == 'POST':
    #     #------------datos de alumno ------------
    #     nombre = request.form['nombre']
    #     apellido = request.form['apellido']
    #     cuil = request.form['cuil']
    #     fechaNac = request.form['fechaNac']
    #     sexo = request.form['sexo']
    #     direccion = request.form['direccion']
    #     telefono  = request.form['telefono']
    #     email = request.form['email']
    #     #tutor_id = request.form['tutor_id']

    #     new_alumno = Alumno(nombre, apellido, cuil, fechaNac, sexo, direccion, telefono, email, new_tutor.id_Tutor)
    #     db.session.add(new_alumno)
    #     db.session.add(new_tutor)
    #     db.session.commit()
    #     flash('Datos guardados correctamente!')
    #     #return render_template('/alumnos/view.html', alumno=alumno)
    #     return redirect(url_for('alumnos.view', alumno=new_alumno.idAlumno)
    colegio = Colegio.query.first()
    if request.method == 'POST':
        try:
        # ------ Capturar datos del formulario HTML - TUTOR-----
            fecha_nac_tutor = datetime.strptime(request.form['fecha_nacimiento_t'], '%Y-%m-%d').date()
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el tutor: {str(e)}', 'danger')
            
            # Los checkboxes en HTML envían "on" si están marcados, o nada si no lo están
            es_legal = request.form.get('legal') == 'on'
            
            nuevo_tutor = Tutor(
                nombre=request.form['nombre_t'],
                apellido=request.form['apellido_t'],
                dni=request.form['dni_t'],
                fecha_nacimiento=fecha_nac_tutor,
                direccion=request.form['direccion_t'],
                telefono=request.form.get('telefono_t'),
                email=request.form.get('email_t'),
                genero=request.form['genero_t'],
                parentesco=request.form.get('parentesco'),
                ocupacion=request.form.get('ocupacion'),
                legal=es_legal
            )
            db.session.add(nuevo_tutor)
            #db.session.add(alumno_tutor.tutor_id==nuevo_tutor.id)  # Agregamos la relación entre Alumno y Tutor
         #---------------Asignar nro de legajo unico--------------
            # Manejo de concurrencia con un bucle de reintentos
            max_reintentos = 3
            for intento in range(max_reintentos):
                try:
                    nuevo_legajo = generar_nuevo_legajo()
                    
                except IntegrityError:
                    # Si dos secretarias guardan exactamente al mismo milisegundo,
                    # una fallará por el constraint UNIQUE del legajo.
                    # Hacemos rollback y el bucle for volverá a intentar generar uno nuevo.
                    db.session.rollback()
                    if intento == max_reintentos - 1:
                        flash({"error": "Error de concurrencia. Por favor, intente de nuevo."}, 'danger')
            #-----------------------------
        #-------captura datos del formulario HTML - ALUMNO-----
            fecha_nac_alumno = datetime.strptime(request.form['fecha_nacimiento_alumno'], '%Y-%m-%d').date()
            nuevo_alumno = Alumno(
            # Campos heredados de Persona
            nombre=request.form['nombre'],
            apellido=request.form['apellido'],
            dni=request.form['dni'],
            fecha_nacimiento=fecha_nac_alumno,
            direccion=request.form['direccion'],
            telefono=request.form['telefono'],
            email=request.form['email'],
            genero=request.form['genero'],
            
            # Campos propios de Alumno
            cuil=request.form['cuil'],
            legajo=nuevo_legajo,
            id_colegio=colegio.id_colegio
        )
            db.session.add(nuevo_alumno)
            # CORRECCIÓN: Flush envía los datos a la BD y genera los IDs (nuevo_alumno.id), 
            # pero no hace un commit definitivo. Si algo falla después, el rollback aún funciona.
            db.session.flush()
            # 5. Agregar la relación en la tabla intermedia
            # Nota: Usamos db.session.execute() para insertar en la tabla Core de SQLAlchemy
            db.session.execute(
                alumno_tutor.insert().values(alumno_id=nuevo_alumno.id, tutor_id=nuevo_tutor.id)
            )
            
            # 6. Confirmar todos los cambios
            db.session.commit()
            
            flash('Tutor y Alumno creados exitosamente.', 'success')
            return redirect(url_for('alumnos.view', alumno=nuevo_alumno.id))  # Redirige a la página de inscripción después de crear el tutor
    return redirect(url_for('alumnos.home')) """

@alumnos.route('/newAlumno', methods=['POST'])
def new_alumno():
    # CORRECCIÓN: Usar .first() para obtener un solo objeto, no una lista
    colegio = Colegio.query.first() 
    
    if request.method == 'POST':
        try:
            # 1. Capturar fechas primero
            fecha_nac_tutor = datetime.strptime(request.form['fecha_nacimiento_t'], '%Y-%m-%d').date()
            fecha_nac_alumno = datetime.strptime(request.form['fecha_nacimiento_alumno'], '%Y-%m-%d').date()
            
            # 2. Crear el Tutor
            es_legal = request.form.get('legal') == 'on'
            nuevo_tutor = Tutor(
                nombre=request.form['nombre_t'],
                apellido=request.form['apellido_t'],
                dni=request.form['dni_t'],
                fecha_nacimiento=fecha_nac_tutor,
                direccion=request.form['direccion_t'],
                telefono=request.form.get('telefono_t'),
                email=request.form.get('email_t'),
                genero=request.form['genero_t'],
                parentesco=request.form.get('parentesco'),
                ocupacion=request.form.get('ocupacion'),
                legal=es_legal
            )
            db.session.add(nuevo_tutor)
            
            # 3. Generar Legajo
            # Idealmente generar_nuevo_legajo() debería ser una función segura que 
            # consulte el último legajo de la BD y le sume 1
            nuevo_legajo = generar_nuevo_legajo()
            
            # 4. Crear el Alumno
            nuevo_alumno = Alumno(
                nombre=request.form['nombre'],
                apellido=request.form['apellido'],
                dni=request.form['dni'],
                fecha_nacimiento=fecha_nac_alumno,
                direccion=request.form['direccion'],
                telefono=request.form['telefono'],
                email=request.form['email'],
                genero=request.form['genero'],
                cuil=request.form['cuil'],
                legajo=nuevo_legajo,
                id_colegio=colegio.id_colegio if colegio else None # Previene errores si no hay colegios
            )
            db.session.add(nuevo_alumno)
            
            # CORRECCIÓN: Flush envía los datos a la BD y genera los IDs (nuevo_alumno.id), 
            # pero no hace un commit definitivo. Si algo falla después, el rollback aún funciona.
            db.session.flush()
            
            # 5. Agregar la relación en la tabla intermedia
            # Nota: Usamos db.session.execute() para insertar en la tabla Core de SQLAlchemy
            db.session.execute(
                alumno_tutor.insert().values(alumno_id=nuevo_alumno.id, tutor_id=nuevo_tutor.id)
            )
            
            # 6. Confirmar todos los cambios
            db.session.commit()
            
            flash('Tutor y Alumno creados exitosamente.', 'success')
            return redirect(url_for('alumnos.view', alumno=nuevo_alumno.id))
            
        except Exception as e:
            # CORRECCIÓN: Si falla CUALQUIER cosa (fechas, BD, etc), entra aquí
            db.session.rollback()
            flash(f'Error al registrar los datos: {str(e)}', 'danger')
            return redirect(url_for('alumnos.home'))

    return redirect(url_for('alumnos.home'))