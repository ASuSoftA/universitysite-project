from app import create_app, db
from app.models.faculty import Faculty

app = create_app()
app.app_context().push()

FACULTIES = [
    'كلية الحاسوب',
    'كلية الهندسة',
    'كلية الطب',
    'كلية العلوم',
]

for name in FACULTIES:
    if not Faculty.query.filter_by(name=name).first():
        db.session.add(Faculty(name=name))

db.session.commit()

print('✔ تم إدخال الكليات بنجاح')
