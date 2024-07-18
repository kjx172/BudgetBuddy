from app import app, db

# Push the application context
with app.app_context():
    db.create_all()
    print("Database tables created.")
