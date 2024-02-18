from Comunidade import app, database
from Comunidade.models import Post, Usuario

with app.app_context():
    database.create_all()