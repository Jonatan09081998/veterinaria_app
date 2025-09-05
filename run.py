from app import create_app, db

app = create_app()

with app.app_context():
    db.create_all()

app.run(port=81, debug=True, host='0.0.0.0')
