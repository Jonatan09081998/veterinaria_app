from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.decorators import rol_requerido
from app.models.mascota import Mascota
from app.models.cita import Cita
from app.models.usuario import Usuario
from app.models.producto import Producto
from app.models.historia_clinica import HistoriaClinica
from app.models.receta import Receta
from app.models.factura import Factura, DetalleFactura
from app import db
from datetime import datetime, date, timedelta

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    return render_template("home.html")

@main_bp.route("/dashboard")
@login_required
def dashboard():
    
    mascotas = Mascota.query.filter_by(id_usuario=current_user.id_usuario).all()

    # Mostrar citas pendientes más antiguas primero
    citas_pendientes = Cita.query.filter_by(
        id_usuario=current_user.id_usuario,
        estado="pendiente"
    ).order_by(Cita.fecha.asc()).all()

     # Mostrar citas atendidas más recientes primero
    citas_atendidas = Cita.query.filter_by(
        id_usuario=current_user.id_usuario,
        estado="atendida"
    ).order_by(Cita.fecha.desc()).all()

    return render_template(
        "dashboard.html",
        mascotas=mascotas,
        citas_pendientes=citas_pendientes,
        citas_atendidas=citas_atendidas
    )

@main_bp.route("/admin")
@login_required
@rol_requerido("admin")
def admin_panel():
    if current_user.rol != "admin":
        flash("No tienes permiso para acceder a este panel", "error")
        return redirect(url_for("main.dashboard"))
    
    # Obtener la fecha actual
    today = date.today()
    
    # Calcular la fecha de mañana para filtrar recetas de hoy
    tomorrow = today + timedelta(days=1)
    
    # Datos para el administrador
    usuarios = Usuario.query.all()
    mascotas = Mascota.query.all()
    citas = Cita.query.filter_by(estado="pendiente").order_by(Cita.fecha.asc()).all()
    productos = Producto.query.all()  # Añadido
    recetas = Receta.query.order_by(Receta.fecha.desc()).limit(10).all()  # Añadido
    
    # Calcular citas de hoy
    citas_hoy = [cita for cita in citas if cita.fecha == today]
    
    # Calcular recetas de hoy (desde hoy 00:00 hasta mañana 00:00)
    recetas_hoy = Receta.query.filter(
        Receta.fecha >= datetime.combine(today, datetime.min.time()),
        Receta.fecha < datetime.combine(tomorrow, datetime.min.time())
    ).all()
    # === PRODUCTOS VENDIDOS ===
    productos_vendidos = db.session.query(
        Producto.nombre.label('nombre_producto'),
        db.func.sum(DetalleFactura.cantidad).label('total_vendido')
    ).join(DetalleFactura, Producto.id_producto == DetalleFactura.id_producto)\
     .group_by(Producto.nombre)\
     .order_by(db.func.sum(DetalleFactura.cantidad).desc())\
     .all()
    

    return render_template("admin_panel.html", 
                          usuarios=usuarios, 
                          mascotas=mascotas, 
                          citas=citas,
                          productos=productos,  # Añadido
                          recetas=recetas,      # Añadido
                          citas_hoy=citas_hoy,
                          recetas_hoy=recetas_hoy,
                          today=today)
    productos_vendidos=productos_vendidos,
                           
# === AÑADIMOS LA RUTA QUE FALTA ===
@main_bp.route('/veterinario')
@login_required
def veterinario_panel():
    if current_user.rol != 'veterinario':
        flash('No tienes permiso para acceder a este panel', 'error')
        return redirect(url_for('main.dashboard'))
    
    today = date.today()
    
    # ✅ Mostrar TODAS las citas pendientes (no solo de hoy)
    citas_pendientes = Cita.query.filter(
        Cita.estado == 'pendiente',
        Cita.id_veterinario == current_user.id_usuario
    ).join(Mascota).all()
    
    # ✅ Citas atendidas (últimas 10)
    citas_atendidas = Cita.query.filter(
        Cita.estado == 'atendida',
        Cita.id_veterinario == current_user.id_usuario
    ).order_by(Cita.fecha.desc()).limit(10).all()
    
    # Recetas recientes
    recetas = Receta.query.join(HistoriaClinica).filter(
        HistoriaClinica.id_veterinario == current_user.id_usuario
    ).order_by(Receta.fecha.desc()).limit(10).all()
    
    return render_template('veterinario_panel.html', 
                          citas_pendientes=citas_pendientes,
                          citas_atendidas=citas_atendidas,
                          recetas=recetas,
                          today=today)
                          
    
@main_bp.route('/veterinario/atender/<int:id_cita>', methods=['POST'])
@login_required
def atender_cita(id_cita):
    if current_user.rol != 'veterinario' and current_user.rol != 'admin':
        flash('No tienes permiso para realizar esta acción', 'error')
        return redirect(url_for('main.dashboard'))
    
    cita = Cita.query.get_or_404(id_cita)
    
    # ✅ DEPURACIÓN: Imprime información para entender el problema
    print(f"DEBUG - Cita ID: {id_cita}")
    print(f"DEBUG - Estado actual: {cita.estado}")
    print(f"DEBUG - Fecha cita: {cita.fecha}, Tipo: {type(cita.fecha)}")
    print(f"DEBUG - Fecha hoy: {date.today()}, Tipo: {type(date.today())}")
    
    # ✅ CORREGIDO: Comparación más flexible de fechas
    if cita.estado != 'pendiente' or cita.fecha < date.today():
        flash(f'Esta cita no puede ser atendida. Estado: {cita.estado}, Fecha: {cita.fecha}', 'error')
        return redirect(url_for('main.veterinario_panel'))
    
    # Verificar que la cita esté asignada a este veterinario (o que sea admin)
    if current_user.rol != 'admin' and cita.id_veterinario != current_user.id_usuario:
        flash('No puedes atender esta cita', 'error')
        return redirect(url_for('main.veterinario_panel'))
    
    # Marcar como atendida
    cita.estado = 'atendida'
    db.session.commit()
    
    flash('✅ Cita atendida correctamente', 'success')
    return redirect(url_for('main.admin_panel' if current_user.rol == 'admin' else 'main.veterinario_panel'))

@main_bp.route('/eliminar_cita/<int:id_cita>', methods=['POST'])
@login_required
@rol_requerido("admin")
def eliminar_cita(id_cita):
    cita = Cita.query.get_or_404(id_cita)
    
    # Verificar que la cita pertenezca al veterinario si no es admin
    if current_user.rol != 'admin' and cita.id_veterinario != current_user.id_usuario:
        flash('No puedes eliminar esta cita', 'error')
        return redirect(url_for('main.veterinario_panel'))
    
    db.session.delete(cita)
    db.session.commit()
    flash('✅ Cita eliminada correctamente', 'success')
    return redirect(url_for('main.admin_panel' if current_user.rol == 'admin' else 'main.veterinario_panel'))

@main_bp.route('/eliminar_cita_atendida/<int:id_cita>', methods=['POST'])
@login_required
@rol_requerido("veterinario")
def eliminar_cita_atendida(id_cita):
    cita = Cita.query.get_or_404(id_cita)
    
    # Verificar que la cita esté atendida
    if cita.estado != 'atendida':
        flash('Solo se pueden eliminar citas atendidas', 'error')
        return redirect(url_for('main.veterinario_panel'))
    
    # Verificar que la cita pertenezca al veterinario
    if cita.id_veterinario != current_user.id_usuario:
        flash('No puedes eliminar esta cita', 'error')
        return redirect(url_for('main.veterinario_panel'))
    
    db.session.delete(cita)
    db.session.commit()
    flash('✅ Cita atendida eliminada correctamente', 'success')
    return redirect(url_for('main.veterinario_panel'))

@main_bp.route('/admin/eliminar_usuario/<int:id_usuario>', methods=['POST'])
@login_required
@rol_requerido("admin")
def eliminar_usuario(id_usuario):
    # ✅ Protección: No permitir auto-eliminación
    if id_usuario == current_user.id_usuario:
        flash('❌ No puedes eliminarte a ti mismo', 'error')
        return redirect(url_for('main.admin_panel'))
    
    usuario = Usuario.query.get_or_404(id_usuario)
    db.session.delete(usuario)
    db.session.commit()
    flash('✅ Usuario eliminado correctamente', 'success')
    return redirect(url_for('main.admin_panel'))