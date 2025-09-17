# init_db.py
from app import create_app
from app import db
from app.models.producto import Producto

app = create_app()

with app.app_context():
    # Elimina productos existentes (opcional)
    # Producto.query.delete()
    # db.session.commit()
    
    # Crea 10 productos de prueba para veterinaria
    productos = [
        Producto(
            nombre='Antipulgas Premium', 
            descripcion='Solución eficaz para eliminar y prevenir pulgas y garrapatas en perros y gatos', 
            precio=59.99, 
            stock=50,
            imagen='antipulgas.jpg'
        ),
        Producto(
            nombre='Alimento Premium para Perros Adultos', 
            descripcion='Alimento balanceado con proteínas de alta calidad, vitaminas y minerales', 
            precio=89.50, 
            stock=30,
            imagen='alimento_perro.jpg'
        ),
        Producto(
            nombre='Juguete Interactivo para Perros', 
            descripcion='Juguete resistente que estimula el instinto de búsqueda y mordida', 
            precio=24.99, 
            stock=40,
            imagen='juguete_perro.jpg'
        ),
        Producto(
            nombre='Collar de Cuero Premium', 
            descripcion='Collar ajustable de cuero genuino con hebilla metálica resistente', 
            precio=35.00, 
            stock=25,
            imagen='collar_cuero.jpg'
        ),
        Producto(
            nombre='Shampoo Especial para Mascotas', 
            descripcion='Fórmula suave con aloe vera y vitamina E para piel sensible', 
            precio=18.75, 
            stock=60,
            imagen='shampoo.jpg'
        ),
        Producto(
            nombre='Vitaminas Completa para Perros', 
            descripcion='Suplemento vitamínico para fortalecer sistema inmunológico y piel', 
            precio=29.99, 
            stock=35,
            imagen='vitaminas.jpg'
        ),
        Producto(
            nombre='Correa Elástica para Perros', 
            descripcion='Correa extensible de 5m con mango ergonómico y bloqueo seguro', 
            precio=19.99, 
            stock=30,
            imagen='correa.jpg'
        ),
        Producto(
            nombre='Cama Ortopédica para Mascotas', 
            descripcion='Cama cómoda con soporte ortopédico para articulaciones', 
            precio=79.99, 
            stock=15,
            imagen='cama.jpg'
        ),
        Producto(
            nombre='Snacks Naturales para Perros', 
            descripcion='Snacks sin conservantes con pollo y arándanos, 100% natural', 
            precio=12.99, 
            stock=55,
            imagen='snacks.jpg'
        )
    ]
    
    db.session.add_all(productos)
    db.session.commit()
    print("✅ 10 productos de prueba agregados exitosamente a la base de datos.")