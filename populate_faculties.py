from app import create_app, db
from app.models.faculty import Faculty

app = create_app()
app.app_context().push()  # ضروري للوصول لقاعدة البيانات

FACULTIES = ['كلية الهندسة',
             'كلية الطب', 
             'كلية العلوم',
             'كلية التجارة', 
             'كلية الزراعة', 
             'كلية المجتمع', 
             'كلية الآداب']

for name in FACULTIES:
    if not Faculty.query.filter_by(name=name).first():
        db.session.add(Faculty(name=name))

db.session.commit()
print("تم تعبئة جدول الكليات بنجاح")
