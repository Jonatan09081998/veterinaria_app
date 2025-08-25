from flask import Blueprint, render_template, request, redirect, url_for, jsonify, send_file
from app.models.usuario import Usuario   # 👈 corregido: "usuarios" y "Usuario"
from app import db
from io import BytesIO
import base64
import json


bp = Blueprint('user', __name__, url_prefix='/user')  # 👈 conviene usar minúsculas en el prefijo

@bp.route('/')
def index():
    data = Usuario.query.all()
    return render_template('users/index.html', data=data)

@bp.route('/js')
def indexjs():
    data = Usuario.query.all()
    result = [user.to_dict() for user in data]  # asegúrate de que tu modelo tenga to_dict()
    return jsonify(result)

@bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        nameUser = request.form['nameUser']
        passwordUser = request.form['passwordUser']        
        new_user = Usuario(nameUser=nameUser, passwordUser=passwordUser)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('user.index'))
    return render_template('users/add.html')

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    user = Usuario.query.get_or_404(id)
    if request.method == 'POST':
        user.nameUser = request.form['nameUser']
        user.passwordUser = request.form['passwordUser']
        db.session.commit()        
        return redirect(url_for('user.index'))
    return render_template('users/edit.html', user=user)

@bp.route('/detail/<int:id>')
def detail(id):
    user = Usuario.query.get_or_404(id)
    return render_template('users/detail.html', user=user)

@bp.route('/delete/<int:id>')
def delete(id):
    user = Usuario.query.get_or_404(id)    
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('user.index'))

@bp.route('/qr/<int:id>')
def generate_qr(id):
    print("Entrando a la ruta de generación de QR para el usuario con ID:", id)
    user = Usuario.query.get_or_404(id)
    qr_code_base64 = user.generate_qr()
    qr_code_img = base64.b64decode(qr_code_base64)  # Decodificar QR desde base64
    return send_file(BytesIO(qr_code_img), mimetype='image/png')

@bp.route('/read_qr', methods=['POST'])
def read_qr():
    from pyzbar.pyzbar import decode
    from PIL import Image
    # resto del código...

    if 'qr_image' not in request.files:
        return "No se ha proporcionado una imagen de QR", 400

    qr_image = request.files['qr_image']
    img = Image.open(qr_image)
    decoded_objects = decode(img)

    if not decoded_objects:
        return "No se pudo leer el código QR", 400

    qr_data = decoded_objects[0].data.decode('utf-8')
    user_data = json.loads(qr_data)
    user_id = user_data.get('ID')

    if not user_id:
        return "El código QR no contiene un ID de usuario válido", 400

    user = Usuario.query.get(user_id)
    if not user:
        return "Usuario no encontrado", 404

    return render_template('users/detail.html', user=user)
