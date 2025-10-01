from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from app.decorators import rol_requerido
from app.models.historia_clinica import HistoriaClinica
from app.models.receta import Receta, RecetaMedicamento
from app.models.mascota import Mascota
from app.models.producto import Producto
from app import db
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

receta_bp = Blueprint('receta', __name__, url_prefix='/recetas')

@receta_bp.route('/crear/<int:id_mascota>', methods=['GET', 'POST'])
@login_required
def crear(id_mascota):
    if current_user.rol != 'veterinario':
        flash('No tienes permiso para crear recetas', 'error')
        return redirect(url_for('main.dashboard'))
    
    mascota = Mascota.query.get_or_404(id_mascota)
    medicamentos = Producto.query.all()
    
    if request.method == 'POST':
        # Crear historia clínica
        historia = HistoriaClinica(
            id_mascota=id_mascota,
            descripcion=request.form['motivo_consulta'],
            tratamiento=request.form.get('sintomas', ''),
            diagnostico=request.form['diagnostico'],
            observaciones=request.form.get('observaciones', ''),
            id_veterinario=current_user.id_usuario
        )
        db.session.add(historia)
        db.session.flush()
        
        # Crear receta
        receta = Receta(id_historia=historia.id_historia)
        db.session.add(receta)
        db.session.flush()
        
        # Agregar medicamentos a la receta
        medicamento_ids = request.form.getlist('medicamento_id')
        cantidades = request.form.getlist('cantidad')
        indicaciones = request.form.getlist('indicaciones')
        
        for i, medicamento_id in enumerate(medicamento_ids):
            if medicamento_id:
                receta_medicamento = RecetaMedicamento(
                    id_receta=receta.id_receta,
                    id_historia=historia.id_historia,
                    id_producto=int(medicamento_id),
                    cantidad=int(cantidades[i]),
                    indicaciones=indicaciones[i]
                )
                db.session.add(receta_medicamento)
        
        db.session.commit()
        flash('✅ Receta creada exitosamente', 'success')
        return redirect(url_for('receta.detalle', id_receta=receta.id_receta))
    
    return render_template('receta/crear.html', mascota=mascota, medicamentos=medicamentos)

@receta_bp.route('/detalle/<int:id_receta>')
@login_required
def detalle(id_receta):
    receta = Receta.query.get_or_404(id_receta)
    
    # Verificar permisos
    if current_user.rol == 'veterinario' and receta.historia_clinica.id_veterinario != current_user.id_usuario:
        flash('No tienes permiso para ver esta receta', 'error')
        return redirect(url_for('main.dashboard'))
    
    if current_user.rol == 'usuario' and receta.historia_clinica.mascota.id_usuario != current_user.id_usuario:
        flash('No tienes permiso para ver esta receta', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('receta/detalle.html', receta=receta)

@receta_bp.route('/descargar_pdf/<int:id_receta>')
@login_required
def descargar_pdf(id_receta):
    receta = Receta.query.get_or_404(id_receta)
    
    # Verificar permisos
    if current_user.rol == 'veterinario' and receta.historia_clinica.id_veterinario != current_user.id_usuario:
        flash('No tienes permiso para descargar esta receta', 'error')
        return redirect(url_for('main.dashboard'))
    
    if current_user.rol == 'usuario' and receta.historia_clinica.mascota.id_usuario != current_user.id_usuario:
        flash('No tienes permiso para descargar esta receta', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Crear PDF con ReportLab
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=40, leftMargin=40,
                           topMargin=60, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Center', alignment=1))
    
    story = []
    
    # Encabezado
    story.append(Paragraph("Clínica Veterinaria Mi Mascota", styles['Title']))
    story.append(Paragraph("Receta Médica", styles['Heading2']))
    story.append(Paragraph(f"Fecha: {receta.fecha.strftime('%d/%m/%Y')}", styles['Normal']))
    story.append(Paragraph("<br/>", styles['Normal']))
    
    # Información de la mascota
    story.append(Paragraph(f"Mascota: {receta.historia_clinica.mascota.nombre}", styles['Normal']))
    story.append(Paragraph(f"Propietario: {receta.historia_clinica.mascota.usuario.nombre}", styles['Normal']))
    story.append(Paragraph(f"Edad: {receta.historia_clinica.mascota.edad} años", styles['Normal']))
    story.append(Paragraph("<br/>", styles['Normal']))
    
    # Diagnóstico
    story.append(Paragraph("Diagnóstico:", styles['Heading3']))
    story.append(Paragraph(receta.historia_clinica.diagnostico, styles['Normal']))
    story.append(Paragraph("<br/>", styles['Normal']))
    
    if receta.historia_clinica.observaciones:
        story.append(Paragraph("Observaciones:", styles['Heading3']))
        story.append(Paragraph(receta.historia_clinica.observaciones, styles['Normal']))
        story.append(Paragraph("<br/>", styles['Normal']))
    
    # Medicamentos
    story.append(Paragraph("Medicamentos Recetados:", styles['Heading3']))
    data = [['Medicamento', 'Cantidad', 'Indicaciones']]
    
    for rm in receta.medicamentos:
        data.append([
            rm.medicamento.nombre,
            str(rm.cantidad),
            rm.indicaciones
        ])
    
    table = Table(data, colWidths=[150, 60, 200])
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
    story.append(Paragraph(f"Firma del Veterinario: {receta.historia_clinica.veterinario.nombre}", styles['Normal']))
    
    # Generar PDF
    doc.build(story)
    
    # Preparar para descarga
    pdf = buffer.getvalue()
    buffer.close()
    
    return send_file(
        BytesIO(pdf),
        download_name=f'receta_{id_receta}.pdf',
        mimetype='application/pdf',
        as_attachment=True
    )
    
@receta_bp.route('/eliminar_receta/<int:id_receta>', methods=['POST'])
@login_required
@rol_requerido("veterinario")
def eliminar_receta(id_receta):
    receta = Receta.query.get_or_404(id_receta)
    
    # Verificar que la receta pertenezca a una historia clínica del veterinario
    if receta.historia_clinica.id_veterinario != current_user.id_usuario:
        flash('No puedes eliminar esta receta', 'error')
        return redirect(url_for('main.veterinario_panel'))
    
    db.session.delete(receta)
    db.session.commit()
    flash('✅ Receta eliminada correctamente', 'success')
    return redirect(url_for('main.veterinario_panel'))    