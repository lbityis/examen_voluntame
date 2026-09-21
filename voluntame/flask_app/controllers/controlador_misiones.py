from flask import Blueprint, render_template, request, redirect, session, flash
from flask_app.models.modelo_mision import Mision

misiones_bp = Blueprint('misiones', __name__)

def obtener_id_usuario():
    return session.get('usuario_id') or session.get('id_usuario') or session.get('user_id')

@misiones_bp.route('/dashboard')
def dashboard():
    id_usuario = obtener_id_usuario()
    # Si no hay sesión, simplemente redirige a la raíz (asegúrate de que en controlador_usuarios / no redirija de nuevo a /dashboard)
    if not id_usuario:
        flash("Debes iniciar sesión para ver esta página.", "login")
        return redirect('/')
    
    misiones = Mision.obtener_todas_futuras()
    return render_template('dashboard.html', misiones=misiones)

@misiones_bp.route('/nueva')
def nueva_mision():
    if not obtener_id_usuario():
        return redirect('/')
    return render_template('nueva_mision.html')

@misiones_bp.route('/crear', methods=['POST'])
def procesar_mision():
    id_usuario = obtener_id_usuario()
    if not id_usuario:
        flash("Sesión no válida o expirada.", "login")
        return redirect('/')

    if not Mision.validar_mision(request.form):
        return redirect('/nueva')

    nombre_campo = request.form.get('nombre') or request.form.get('titulo')

    data = {
        "nombre": nombre_campo,
        "titulo": nombre_campo,
        "fecha": request.form.get('fecha'),
        "voluntarios_necesarios": request.form.get('voluntarios_necesarios'),
        "descripcion": request.form.get('descripcion'),
        "id_usuario": id_usuario,
        "usuario_id": id_usuario
    }

    Mision.guardar(data)
    return redirect('/dashboard')

@misiones_bp.route('/ver/<int:id_mision>')
def ver_mision(id_mision):
    if not obtener_id_usuario():
        return redirect('/')

    data = {"id_mision": id_mision}
    mision = Mision.obtener_por_id_con_relaciones(data)
    return render_template('ver_mision.html', mision=mision)

@misiones_bp.route('/unirse/<int:id_mision>')
def unirse_mision(id_mision):
    id_usuario = obtener_id_usuario()
    if not id_usuario:
        return redirect('/')

    data = {
        "id_usuario": id_usuario,
        "usuario_id": id_usuario,
        "id_mision": id_mision
    }
    Mision.agregar_voluntario(data)
    return redirect(f'/ver/{id_mision}')

@misiones_bp.route('/editar/<int:id_mision>')
def editar_mision(id_mision):
    id_usuario = obtener_id_usuario()
    if not id_usuario:
        return redirect('/')

    data = {"id_mision": id_mision}
    mision = Mision.obtener_por_id_con_relaciones(data)

    if not mision:
        return redirect('/dashboard')

    creador_id = getattr(mision, 'id_usuario', None) or getattr(mision, 'usuario_id', None)
    if id_usuario != creador_id:
        flash("No tienes permiso para editar misiones de otros usuarios.", "login")
        return redirect('/dashboard')

    return render_template('editar_mision.html', mision=mision)

@misiones_bp.route('/actualizar/<int:id_mision>', methods=['POST'])
def actualizar_mision(id_mision):
    if not obtener_id_usuario():
        return redirect('/')

    if not Mision.validar_mision(request.form):
        return redirect(f'/editar/{id_mision}')

    nombre_campo = request.form.get('nombre') or request.form.get('titulo')

    data = {
        "id_mision": id_mision,
        "nombre": nombre_campo,
        "titulo": nombre_campo,
        "fecha": request.form.get('fecha'),
        "voluntarios_necesarios": request.form.get('voluntarios_necesarios'),
        "descripcion": request.form.get('descripcion')
    }

    Mision.actualizar(data)
    return redirect('/dashboard')

@misiones_bp.route('/borrar/<int:id_mision>')
def borrar_mision(id_mision):
    id_usuario = obtener_id_usuario()
    if not id_usuario:
        return redirect('/')

    data = {"id_mision": id_mision}
    mision = Mision.obtener_por_id_con_relaciones(data)

    if mision:
        creador_id = getattr(mision, 'id_usuario', None) or getattr(mision, 'usuario_id', None)
        if id_usuario == creador_id:
            Mision.eliminar(data)
        else:
            flash("No puedes borrar una misión que no te pertenece.", "login")

    return redirect('/dashboard')