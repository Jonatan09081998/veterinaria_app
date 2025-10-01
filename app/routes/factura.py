# app/routes/factura.py
from flask import Blueprint, render_template, redirect, url_for, flash, send_file, request
from flask_login import login_required, current_user
from app.decorators import rol_requerido
from app.models.factura import Factura, DetalleFactura
from app.models.carrito import Carrito, CarritoItem
from app.models.producto import Producto
from app import db
import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

factura_bp = Blueprint('factura', __name__, url_prefix='/factura')

@factura_bp.route('/pasarela')
@login_required
def pasarela():
    # Obtener carrito del usuario
    carrito = Carrito.query.filter_by(id_usuario=current_user.id_usuario).first()
    
    if not carrito or not carrito.items:
        flash('Tu carrito está vacío', 'warning')
        return redirect(url_for('carrito.ver'))
    
    # Calcular total
    total = sum(item.cantidad * item.producto.precio for item in carrito.items)
    
    return render_template('factura/pasarela_pago.html', 
                          carrito_items=carrito.items, 
                          total=total)

@factura_bp.route('/procesar_pago', methods=['POST'])
@login_required
def procesar_pago():
    # Obtener carrito del usuario
    carrito = Carrito.query.filter_by(id_usuario=current_user.id_usuario).first()
    
    if not carrito or not carrito.items:
        flash('Tu carrito está vacío', 'warning')
        return redirect(url_for('carrito.ver'))
    
    # Calcular total
    total = sum(item.cantidad * item.producto.precio for item in carrito.items)
    
    # Obtener datos del formulario
    nombre = request.form.get('nombre')
    email = request.form.get('email')
    direccion = request.form.get('direccion')
    telefono = request.form.get('telefono')
    metodo_pago = request.form.get('metodo_pago')
    
    # Crear factura
    factura = Factura(
        fecha=datetime.datetime.now().date(),
        total=total,
        estado='pagada',  # Simulamos pago exitoso
        id_usuario=current_user.id_usuario,
        nombre_cliente=nombre,
        email_cliente=email,
        direccion_envio=direccion,
        telefono_cliente=telefono,
        metodo_pago=metodo_pago
    )
    db.session.add(factura)
    db.session.flush()  # Para obtener el id_factura
    
    # Crear detalles de la factura
    for item in carrito.items:
        detalle = DetalleFactura(
            id_factura=factura.id_factura,
            id_producto=item.id_producto,
            cantidad=item.cantidad,
            precio_unitario=item.producto.precio,
            
        )
        db.session.add(detalle)
        
        # Actualizar stock del producto
        producto = Producto.query.get(item.id_producto)
        if producto:
            producto.stock -= item.cantidad
    
    # Vaciar carrito
    CarritoItem.query.filter_by(id_carrito=carrito.id_carrito).delete()
    
    db.session.commit()
    flash('✅ ¡Pago procesado con éxito! Tu factura ha sido generada.', 'success')
    return redirect(url_for('factura.detalle', id_factura=factura.id_factura))

@factura_bp.route('/detalle/<int:id_factura>')
@login_required
def detalle(id_factura):
    factura = Factura.query.get_or_404(id_factura)
    
    # ✅ Solo el dueño de la factura o el administrador pueden verla
    if factura.id_usuario != current_user.id_usuario and current_user.rol != 'admin':
        flash('No tienes permiso para ver esta factura', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('factura/detalle.html', factura=factura)

@factura_bp.route('/descargar_pdf/<int:id_factura>')
@login_required
def descargar_pdf(id_factura):
    factura = Factura.query.get_or_404(id_factura)
    if factura.id_usuario != current_user.id_usuario:
        flash('No tienes permiso para descargar esta factura', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Crear PDF con ReportLab
    buffer = BytesIO()
    
    # Configuración del documento
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40, leftMargin=40,
        topMargin=60, bottomMargin=40
    )
    
    # Estilos
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Center', alignment=1))
    styles.add(ParagraphStyle(name='Right', alignment=2))
    
    # Contenido del PDF
    story = []
    
    # Encabezado
    story.append(Paragraph("Veterinaria Mi Mascota", styles['Title']))
    story.append(Paragraph(f"Factura #{id_factura}", styles['Heading2']))
    story.append(Paragraph(f"Fecha: {factura.fecha.strftime('%d/%m/%Y')}", styles['Normal']))
    story.append(Paragraph("<br/>", styles['Normal']))
    
    # Información del cliente
    story.append(Paragraph(f"Cliente: {factura.nombre_cliente}", styles['Normal']))
    story.append(Paragraph(f"Dirección: {factura.direccion_envio or 'N/A'}", styles['Normal']))
    story.append(Paragraph(f"Teléfono: {factura.telefono_cliente or 'N/A'}", styles['Normal']))
    story.append(Paragraph(f"Método de Pago: {factura.metodo_pago or 'N/A'}", styles['Normal']))
    story.append(Paragraph("<br/>", styles['Normal']))
    
    # Tabla de productos
    data = [['Producto', 'Cantidad', 'Precio Unitario', 'Total']]
    
    for detalle in factura.detalles:
        data.append([
            detalle.producto.nombre,
            str(detalle.cantidad),
            "${:.2f}".format(detalle.precio_unitario),
            "${:.2f}".format(detalle.cantidad * detalle.precio_unitario)
        ])
    
    # Añadir fila del total
    data.append(['', '', 'TOTAL:', "${:.2f}".format(factura.total)])
    
    # Crear tabla
    table = Table(data, colWidths=[150, 60, 100, 80])
    
    # Estilo de la tabla
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    story.append(Paragraph("<br/><br/>", styles['Normal']))
    story.append(Paragraph("Gracias por su compra. Esperamos verlo de nuevo pronto.", styles['Normal']))
    
    # Generar PDF
    doc.build(story)
    
    # Preparar para descarga
    pdf = buffer.getvalue()
    buffer.close()
    
    return send_file(
        BytesIO(pdf),
        download_name=f'factura_{id_factura}.pdf',
        mimetype='application/pdf',
        as_attachment=True
    )
@factura_bp.route('/listar')
@login_required
@rol_requerido("admin")
def listar_facturas():
    # Obtener todas las facturas (ordenadas por fecha descendente)
    facturas = Factura.query.order_by(Factura.fecha.desc()).all()
    return render_template('factura/listar.html', facturas=facturas)   
@factura_bp.route('/eliminar/<int:id_factura>', methods=['POST'])
@login_required
@rol_requerido("admin")
def eliminar_factura(id_factura):
    factura = Factura.query.get_or_404(id_factura)
    
    # Eliminar todos los detalles de la factura primero (por integridad referencial)
    DetalleFactura.query.filter_by(id_factura=id_factura).delete()
    
    # Luego eliminar la factura
    db.session.delete(factura)
    db.session.commit()
    
    flash('✅ Factura eliminada correctamente', 'success')
    return redirect(url_for('factura.listar_facturas')) 
