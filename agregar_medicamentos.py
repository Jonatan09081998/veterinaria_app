from app import create_app, db
from app.models.producto import Producto

app = create_app()
with app.app_context():
    # Lista de medicamentos
    medicamentos = [
        {
            "nombre": "Amoxicilina Veterinaria",
            "descripcion": "Antibiótico de amplio espectro para infecciones bacterianas en mascotas",
            "precio": 12.50,
            "stock": 30,
            "imagen": "amoxicilina.jpg"
        },
        {
            "nombre": "Ivermectina",
            "descripcion": "Antiparasitario para el tratamiento de ácaros, garrapatas y otros parásitos",
            "precio": 8.75,
            "stock": 25,
            "imagen": "ivermectina.jpg"
        },
        {
            "nombre": "Ketofast",
            "descripcion": "Antiinflamatorio no esteroideo para el alivio del dolor y la inflamación",
            "precio": 15.99,
            "stock": 20,
            "imagen": "ketofast.jpg"
        },
        {
            "nombre": "Paracetamol Veterinario",
            "descripcion": "Analgésico y antipirético para el alivio del dolor leve a moderado",
            "precio": 6.50,
            "stock": 40,
            "imagen": "paracetamol.jpg"
        },
        {
            "nombre": "Advantage",
            "descripcion": "Tratamiento tópico para control de pulgas en perros y gatos",
            "precio": 18.99,
            "stock": 15,
            "imagen": "advantage.jpg"
        }
    ]
    
    # Crear y guardar los medicamentos
    for med_data in medicamentos:
        # Verificar si ya existe el medicamento
        medicamento = Producto.query.filter_by(nombre=med_data["nombre"]).first()
        if not medicamento:
            medicamento = Producto(**med_data)
            db.session.add(medicamento)
    
    db.session.commit()
    print("¡5 medicamentos agregados exitosamente!")