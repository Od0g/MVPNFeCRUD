from app import create_app, db
from app.models import User

app = create_app()
app.app_context().push()

db.create_all()

admin = User(username='admin', role='admin')
admin.set_password('admin123')
db.session.add(admin)
db.session.commit()
